// Stripe webhook handler for Gas Safe App
// Receives checkout.session.completed events and logs subscription details
// Also syncs subscription status to Supabase when configured
// Endpoint: /.netlify/functions/stripe-webhook

const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

// Supabase admin client for server-side writes (bypasses RLS)
let supabaseAdmin = null;
if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY) {
  const { createClient } = require("@supabase/supabase-js");
  supabaseAdmin = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const sig = event.headers["stripe-signature"];
  let stripeEvent;

  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error("⚠️ Webhook signature verification failed:", err.message);
    return { statusCode: 400, body: `Webhook Error: ${err.message}` };
  }

  // Handle checkout session completed
  if (stripeEvent.type === "checkout.session.completed") {
    const session = stripeEvent.data.object;
    const customerEmail = session.customer_email || session.customer_details?.email;
    const clientRef = session.client_reference_id; // The app username
    const subscriptionId = session.subscription;
    const customerId = session.customer;

    console.log("✅ Checkout completed:", {
      customerEmail,
      clientRef,
      subscriptionId,
      customerId,
    });

    // Store the username in Stripe customer metadata so we can look it up later
    if (customerId && clientRef) {
      try {
        await stripe.customers.update(customerId, {
          metadata: { app_username: clientRef },
        });
        console.log(`📝 Updated customer ${customerId} metadata with username: ${clientRef}`);
      } catch (err) {
        console.error("Failed to update customer metadata:", err.message);
      }
    }

    // If we have a subscription, add plan info to its metadata too
    if (subscriptionId) {
      try {
        const subscription = await stripe.subscriptions.retrieve(subscriptionId);
        const priceId = subscription.items.data[0]?.price?.id;
        const productId = subscription.items.data[0]?.price?.product;

        // Determine plan name from product
        let planName = "unknown";
        if (productId) {
          const product = await stripe.products.retrieve(productId);
          if (product.name.includes("Lite")) planName = "lite";
          else if (product.name.includes("Pro+")) planName = "proplus";
          else if (product.name.includes("Pro")) planName = "pro";
        }

        await stripe.subscriptions.update(subscriptionId, {
          metadata: { app_username: clientRef, plan: planName },
        });

        console.log(`📝 Subscription ${subscriptionId} tagged: ${clientRef} → ${planName}`);

        // Sync to Supabase if configured
        if (supabaseAdmin && clientRef) {
          try {
            // Find the Supabase user by username in profiles
            const { data: profile } = await supabaseAdmin
              .from("profiles")
              .select("user_id")
              .eq("username", clientRef)
              .single();

            if (profile) {
              await supabaseAdmin
                .from("profiles")
                .update({
                  plan: planName,
                  subscription_active: true,
                  stripe_customer_id: customerId,
                  stripe_subscription_id: subscriptionId,
                })
                .eq("user_id", profile.user_id);
              console.log(`🗄️ Supabase profile updated: ${clientRef} → ${planName}`);
            }
          } catch (dbErr) {
            console.error("Failed to update Supabase profile:", dbErr.message);
          }
        }
      } catch (err) {
        console.error("Failed to update subscription metadata:", err.message);
      }
    }
  }

  // Handle subscription cancelled/deleted
  if (stripeEvent.type === "customer.subscription.deleted") {
    const subscription = stripeEvent.data.object;
    const username = subscription.metadata?.app_username;
    console.log(`❌ Subscription cancelled for: ${username || "unknown"}`);

    // Downgrade in Supabase
    if (supabaseAdmin && username) {
      try {
        const { data: profile } = await supabaseAdmin
          .from("profiles")
          .select("user_id")
          .eq("username", username)
          .single();
        if (profile) {
          await supabaseAdmin
            .from("profiles")
            .update({ plan: "lite", subscription_active: false })
            .eq("user_id", profile.user_id);
          console.log(`🗄️ Supabase: ${username} downgraded to lite`);
        }
      } catch (dbErr) {
        console.error("Failed to downgrade in Supabase:", dbErr.message);
      }
    }
  }

  // Handle invoice payment failed
  if (stripeEvent.type === "invoice.payment_failed") {
    const invoice = stripeEvent.data.object;
    console.log(`⚠️ Payment failed for customer: ${invoice.customer}`);
  }

  return {
    statusCode: 200,
    body: JSON.stringify({ received: true }),
  };
};
