// Annual CP12 Reminder System — Gas Safe App
// Sends email reminders to landlords when their gas safety certificate is expiring
// Triggered via scheduled Netlify Function or manual HTTP call
//
// Endpoint: /.netlify/functions/annual-reminders
// Requires: SUPABASE_URL, SUPABASE_SERVICE_KEY, GMAIL_SEND_ENABLED (optional)

exports.handler = async (event) => {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  };

  // Only works if Supabase is configured
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ message: "Supabase not configured — skipping reminders" }),
    };
  }

  const { createClient } = require("@supabase/supabase-js");
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );

  try {
    // Find all certificates that are CP12 / Gas Safety Records
    // and were saved approximately 11 months ago (30 days before expiry)
    const now = new Date();
    const elevenMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 11, now.getDate());
    const twelveMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 12, now.getDate());

    // Window: certs saved between 11-12 months ago (due for renewal in next 30 days)
    const { data: expiringCerts, error } = await supabase
      .from("certificates")
      .select("*")
      .in("cert_type", ["gsc", "dsr", "cp12", "landlord"])
      .gte("saved_at", twelveMonthsAgo.toISOString())
      .lte("saved_at", elevenMonthsAgo.toISOString());

    if (error) {
      console.error("Error querying certs:", error.message);
      return { statusCode: 500, headers, body: JSON.stringify({ error: error.message }) };
    }

    if (!expiringCerts || !expiringCerts.length) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ message: "No expiring certificates found", count: 0 }),
      };
    }

    const reminders = [];

    for (const cert of expiringCerts) {
      const certData = cert.data || {};
      const clientEmail = certData.clientEmail;
      const clientName = certData.clientName || "Tenant/Landlord";
      const address = [certData.instAddr1, certData.instAddr2, certData.instPostcode]
        .filter(Boolean)
        .join(", ");
      const certDate = new Date(cert.saved_at).toLocaleDateString("en-GB");
      const expiryDate = new Date(
        new Date(cert.saved_at).getFullYear() + 1,
        new Date(cert.saved_at).getMonth(),
        new Date(cert.saved_at).getDate()
      ).toLocaleDateString("en-GB");

      // Get engineer's profile for company details
      const { data: profile } = await supabase
        .from("profiles")
        .select("company_name, company_tel, company_email, engineer_name")
        .eq("user_id", cert.user_id)
        .single();

      const companyName = profile?.company_name || "Your Gas Engineer";
      const companyTel = profile?.company_tel || "";
      const companyEmail = profile?.company_email || "";
      const engineerName = profile?.engineer_name || "";

      reminders.push({
        certId: cert.id,
        clientEmail,
        clientName,
        address,
        certDate,
        expiryDate,
        companyName,
        companyTel,
        companyEmail,
        engineerName,
        userId: cert.user_id,
      });

      // Log the reminder (in future, this would send an email)
      console.log(
        `📧 Reminder: ${clientName} at ${address} — cert from ${certDate} expires ${expiryDate}`
      );
    }

    // For now, return the list of reminders that would be sent
    // Email sending will be wired up when Gmail API or SMTP is configured
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        message: `Found ${reminders.length} expiring certificates`,
        count: reminders.length,
        reminders: reminders.map((r) => ({
          client: r.clientName,
          address: r.address,
          expires: r.expiryDate,
          engineer: r.engineerName,
          hasEmail: !!r.clientEmail,
        })),
      }),
    };
  } catch (err) {
    console.error("Annual reminders error:", err.message);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
