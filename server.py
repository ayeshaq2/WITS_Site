import stripe
import json
import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/membership')
def membership():
  return render_template('membership.html')

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
    success_url='http://localhost:5000/success?id={CHECKOUT_SESSION_ID}',
    cancel_url='http://localhost:5000/cancel',
    submit_type='donate',
    payment_method_types=['card'],
    customer_email=data['uwoEmail'],
    metadata={'customerName' : data['name']},
    line_items=[{
      'quantity': 1,
      'name': "WITS 2020/21 Club Membership",
      'currency': 'cad',
      'amount': 1500,
    }]
  )
  return jsonify(session)


# TODO: Put this in the dotenv soon when deploying to prod!
endpoint_secret = "whsec_bFLSqri5DuglBrtbecP06DEOvXD3m8Hb"
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
    customer_id = checkout_session_obj['customer']
    update_response = stripe.Customer.modify(customer_id, name=customer_name)
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

# Start server
if __name__ == '__main__':
    app.run(port=4242)