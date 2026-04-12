// Admin Dashboard API — Gas Safe App
// Returns aggregated data for the admin: all engineers, certs, subscription status
// Secured by admin API key
//
// Endpoint: /.netlify/functions/admin-dashboard?key=ADMIN_API_KEY
// Requires: SUPABASE_URL, SUPABASE_SERVICE_KEY, ADMIN_API_KEY

exports.handler = async (event) => {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Content-Type": "application/json",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers, body: "" };
  }

  // Auth check
  const apiKey = event.queryStringParameters?.key;
  if (!apiKey || apiKey !== process.env.ADMIN_API_KEY) {
    return { statusCode: 401, headers, body: JSON.stringify({ error: "Unauthorized" }) };
  }

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ error: "Supabase not configured" }),
    };
  }

  const { createClient } = require("@supabase/supabase-js");
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );

  const action = event.queryStringParameters?.action || "overview";

  try {
    if (action === "overview") {
      // Get all profiles (engineers)
      const { data: profiles } = await supabase
        .from("profiles")
        .select("id, user_id, username, display_name, company_name, engineer_name, gas_safe_no, plan, subscription_active, registered_at");

      // Get cert counts per user
      const { data: certs } = await supabase
        .from("certificates")
        .select("user_id, cert_type, saved_at");

      // Get ticket counts
      const { data: tickets } = await supabase
        .from("support_tickets")
        .select("id, ticket_ref, ticket_type, status, created_at, username");

      // Aggregate
      const certsByUser = {};
      (certs || []).forEach((c) => {
        if (!certsByUser[c.user_id]) certsByUser[c.user_id] = { total: 0, thisMonth: 0, types: {} };
        certsByUser[c.user_id].total++;
        const now = new Date();
        if (new Date(c.saved_at).getMonth() === now.getMonth() &&
            new Date(c.saved_at).getFullYear() === now.getFullYear()) {
          certsByUser[c.user_id].thisMonth++;
        }
        certsByUser[c.user_id].types[c.cert_type] =
          (certsByUser[c.user_id].types[c.cert_type] || 0) + 1;
      });

      const engineers = (profiles || []).map((p) => ({
        username: p.username,
        name: p.engineer_name || p.display_name || "Unknown",
        company: p.company_name || "",
        gasSafeNo: p.gas_safe_no || "",
        plan: p.plan,
        active: p.subscription_active,
        registeredAt: p.registered_at,
        certs: certsByUser[p.user_id] || { total: 0, thisMonth: 0, types: {} },
      }));

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          totalEngineers: engineers.length,
          totalCerts: (certs || []).length,
          openTickets: (tickets || []).filter((t) => t.status === "open").length,
          engineers,
          recentTickets: (tickets || []).slice(0, 20),
        }),
      };
    }

    if (action === "certs") {
      // Get all certs with optional filters
      const userId = event.queryStringParameters?.userId;
      const certType = event.queryStringParameters?.type;
      const search = event.queryStringParameters?.search;

      let query = supabase
        .from("certificates")
        .select("*")
        .order("saved_at", { ascending: false })
        .limit(100);

      if (userId) query = query.eq("user_id", userId);
      if (certType) query = query.eq("cert_type", certType);

      const { data: certs } = await query;

      // If search term, filter by address/name in the data JSONB
      let results = certs || [];
      if (search) {
        const s = search.toLowerCase();
        results = results.filter((c) => {
          const d = c.data || {};
          return (
            (d.clientName || "").toLowerCase().includes(s) ||
            (d.instAddr1 || "").toLowerCase().includes(s) ||
            (d.instAddr2 || "").toLowerCase().includes(s) ||
            (d.instPostcode || "").toLowerCase().includes(s) ||
            (d.fileRef || "").toLowerCase().includes(s) ||
            (c.file_ref || "").toLowerCase().includes(s)
          );
        });
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          count: results.length,
          certs: results.map((c) => ({
            id: c.id,
            type: c.cert_type,
            fileRef: c.file_ref || c.data?.fileRef || "",
            clientName: c.data?.clientName || "",
            address: [c.data?.instAddr1, c.data?.instAddr2, c.data?.instPostcode]
              .filter(Boolean)
              .join(", "),
            savedAt: c.saved_at,
            engineerUserId: c.user_id,
          })),
        }),
      };
    }

    if (action === "cert-detail") {
      const certId = event.queryStringParameters?.id;
      if (!certId) {
        return { statusCode: 400, headers, body: JSON.stringify({ error: "Missing cert id" }) };
      }

      const { data: cert } = await supabase
        .from("certificates")
        .select("*")
        .eq("id", certId)
        .single();

      if (!cert) {
        return { statusCode: 404, headers, body: JSON.stringify({ error: "Certificate not found" }) };
      }

      return { statusCode: 200, headers, body: JSON.stringify(cert) };
    }

    return { statusCode: 400, headers, body: JSON.stringify({ error: "Unknown action" }) };
  } catch (err) {
    console.error("Admin dashboard error:", err.message);
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};
