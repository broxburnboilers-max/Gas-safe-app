// Check subscription status for a Gas Safe App user
// Called by the app on login to verify subscription is active
// Endpoint: /.netlify/functions/check-subscription?username=user@example.com

const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  // CORS headers for the app
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Content-Type": "application/json",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers, body: "" };
  }

  if (event.httpMethod !== "GET") {
    return { statusCode: 405, headers, body: JSON.stringify({ error: "Method Not Allowed" }) };
  }

  const username = event.queryStringParameters?.username;
  if (!username) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({ error: "Missing username parameter" }),
    };
  }

  try {
    // Search for Stripe customers with this username in metadata
    const customers = await stripe.customers.search({
      query: `metadata["app_username"]:"${username}"`,
    });

    if (!customers.data.length) {
      // Also try by email
      const byEmail = await stripe.customers.list({ email: username, limit: 1 });
      if (!byEmail.data.length) {
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            active: false,
            plan: null,
            message: "No subscription found",
          }),
        };
      }
      customers.data = byEmail.data;
    }

    const customerId = customers.data[0].id;

    // Get active subscriptions for this customer
    const subscriptions = await stripe.subscriptions.list({
      customer: customerId,
      status: "active",
      limit: 1,
    });

    if (!subscriptions.data.length) {
      // Check for trialing subscriptions too
      const trialing = await stripe.subscriptions.list({
        customer: customerId,
        status: "trialing",
        limit: 1,
      });

      if (!trialing.data.length) {
        return {
          statusCode: 200,
          headers,
          body: JSON.stringify({
            active: false,
            plan: null,
            message: "No active subscription",
          }),
        };
      }
      subscriptions.data = trialing.data;
    }

    const sub = subscriptions.data[0];
    const plan = sub.metadata?.plan || "unknown";
    const currentPeriodEnd = new Date(sub.current_period_end * 1000).toISOString();

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        active: true,
        plan,
        status: sub.status,
        currentPeriodEnd,
        subscriptionId: sub.id,
      }),
    };
  } catch (err) {
    console.error("Error checking subscription:", err.message);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: "Failed to check subscription" }),
    };
  }
};
