import stripe
import json
import os
from flask import Flask, render_template, jsonify, request, redirect
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
from hubspot.crm.contacts.exceptions import ApiException
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Loading secrets
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
hubspot = HubSpot(api_key=os.getenv('HUBSPOT_SECRET_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/membership')
def membership():
    return redirect("https://tally.so/r/waWXX2", code=302)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/initiatives')
def initiatives():
  return render_template('initiatives.html')

@app.route('/partners')
def partners():
  return render_template('partners.html')

@app.route('/blog')
def blog():
  return render_template('blog.html')

@app.route('/ada')
def ada():
  return render_template('ada.html')

@app.route('/events')
def events():
  return render_template('events.html')

@app.route('/success')
def success():
  return render_template('success.html')

@app.route('/cancel')
def cancel():
  return render_template('cancel.html')



# Creating checkout sessions
@app.route('/create-session', methods=['POST'])
def create_session():
  print("Create session is called"); 
  data = json.loads(request.data)
  print(f'user given name: {data}')
  session = stripe.checkout.Session.create(
    success_url='https://wits-uwo.ca/?paymentSuccess=1',
    cancel_url='http://wits-uwo.ca/',
    payment_method_types=['card'],
    customer_email=data['uwoEmail'],
    metadata={'customerName' : data['name']},
    line_items=[{
      'quantity': 1,
      'price': "price_1HSDP8I0omsarzuVHy5RQSYL",
    }],
    mode="payment",
  )
  return jsonify(session)

endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
@app.route('/webhook', methods=['POST'])
def webhook():
  event = None
  payload = request.data

  try:
    event = json.loads(payload)
  except:
    # TODO: Have error send to WITS email, alerting about system not working
    print("Webhook error occured, ignoring request" + str(e))
    return jsonify(success=True)
  
  # Verifying request is from STRIPE
  if endpoint_secret:
    sig_header = request.headers.get('stripe-signature')
    try:
      event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as e:
      # TODO: Have this error send out as to WITS email also, potential misuse
      print("Webhook signature verification failed " + str(e))
      return jsonify(success=True)
  
  # Grab metadata and post full name to associated customer id!
  if event and event['type'] == 'checkout.session.completed':
    checkout_session_obj = event['data']['object']
    print(f'Recieved following data {checkout_session_obj}')
    customer_name = checkout_session_obj['metadata']['customerName']
    customer_email = checkout_session_obj['customer_email']
    customer_id = checkout_session_obj['customer']
    update_response = stripe.Customer.modify(customer_id, name=customer_name)
    # Push contact details onto hubspot
    create_hubspot_contact(customer_email, customer_name)
  else:
    # We don't handle for this event, we leave it, don't need email alerts for this
    print(f"Unhandled event type {event['type']}")

  return jsonify(success=True)


# Retrieving sessions 
@app.route('/retrieve-session', methods=['POST'])
def retrieve_session():
  session = stripe.checkout.Session.retrieve(
    request.args['id'],
    expand=['payment_intent'],
  )
  return jsonify(session)


def create_hubspot_contact(email, name):
  name = name.split()
  first_name = name[0]
  last_name = ""
  # Naiive error handling if user only provides first name
  if (len(name) >= 2):
     last_name = name[1]
  try:
    simple_public_object_input = SimplePublicObjectInput(
        properties={"email": email,
                    "firstname": first_name,
                    "lastname": last_name}
    )
    api_response = hubspot.crm.contacts.basic_api.create(
        simple_public_object_input=simple_public_object_input
    )
  except ApiException as e:
    print("Exception when creating contact: %s\n" % e)

# Start server
if __name__ == '__main__':
    app.run(host='0.0.0.0')
