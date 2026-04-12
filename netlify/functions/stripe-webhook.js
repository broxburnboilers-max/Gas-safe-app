// Stripe webhook handler for Gas Safe App
// Receives checkout.session.completed events and logs subscription details
// Endpoint: /.netlify/functions/stripe-webhook

const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

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
