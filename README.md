# WITS_Site

# Checkout Flow

The website uses Stripe Checkout to proces payments. All processing, authentication, and more is done on Stripe's end. All we do is redirect the user to the Stripe checkout page and back to our website. Since Stripe Checkout does not allow for custom fields, we ask the customer for their full name and email beforehand so we can update their customer record later. This is important for us as having their preferred name and email in our records allows us to integrate with Hubspot seamlessly with no manual effort.

When we create a checkout session, the user metadata is appended to Stripe Checkout data. It is propogated throughout all steps of the process. We then utilize webhooks to actively listen for whenever a checkout.session.completed event occurs, which is our cue we have a new paying member to WITS. When the event triggers, our listener takes in the event data and updates the customer record with the corresponding user metadata we obtained earlier. The Stripe Customer record now contains their preferred name, email, and confirmation they are a WITS member. 

Here's a diagram to illustrate how the components work:
![alt text](<DiagramWITS.jpg>)
