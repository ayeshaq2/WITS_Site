# Women in Technology Website

This is the repo for the live version of the WITS website at www.wits-uwo.ca. 

.env file should never be pushed on the repo. It exists only on the Digital Ocean droplet. All references to it should be done using the `os` module in Python. See `server.py` for how to reference the keys in a safe manner. It contains sensitive API keys that cannot be shared with malicious attackers. 

# Testing
This repo contains a Heroku valid procfile that you can use to test changes before pushing them to production. Once changes are pushed to the repo, open up Heroku and deploy this repo as an app. A project specific url should be created that you can use to test any changes you've made. 

If you'd like to test locally instead, execute the following steps in the root directory of the repo:
```
export FLASK_APP=server.py
flask run
```

# Deployment 
All DNS records are managed on Digital Ocean, they cannot be changed on GoDaddy as it's been delegated to Digital Ocean (to undo this, change nameservers on GoDaddy for the domain to default). All changes to DNS records should be made on Digital Ocean. 

This repo is deployed on a Digital Ocean droplet, using nginx and gunicorn for production. SSL certificate is self signed using certbot (https://letsencrypt.org/). Ideally, there should be no git pushes from the prod server to this repository. This is to prevent any accidental leaks of private information on this repo.

To push changes to production, follow these steps:
+ Push changes to this repo
+ Login to droplet using password
+ git pull changes
+ Run `sudo systemctl restart wits_site`
+ Run `sudo systemctl restart nginx`

Changes will be deployed and should be applied within ~1-2 minutes of restarting.

System uses systemd unit files to run the server processes. Here are the paths of some important files for debugging:
```
/etc/systemd/system/wits_site.service
/WITS_Site/wsgi.py
/etc/nginx/sites-available/wits_site
```
If any changes are made to the nginx site-available wits_site file, be sure to run: `sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled`, to apply those changes. Moreover, also run `sudo nginx -t` to ensure changes do not contain syntax errors.

Should errors occurs, you can check these logs:
+ `sudo less /var/log/nginx/error.log`: checks the Nginx error logs.
+ `sudo less /var/log/nginx/access.log`: checks the Nginx access logs.
+ `sudo journalctl -u nginx`: checks the Nginx process logs.
+ `sudo journalctl -u wits_site`: checks the Flask app’s Gunicorn logs.

You can read more about deployment process here: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04


# Checkout Flow

The website uses Stripe Checkout to process payments. All processing, authentication, and more is done on Stripe's end. All we do is redirect the user to the Stripe checkout page and back to our website. Since Stripe Checkout does not allow for custom fields, we ask the customer for their full name and email beforehand so we can update their customer record later. This is important for us as having their preferred name and email in our records allows us to integrate with Hubspot seamlessly with no manual effort.

When we create a checkout session, the user metadata is appended to Stripe Checkout data. It is propogated throughout all steps of the process. We then utilize webhooks to actively listen for whenever a checkout.session.completed event occurs, which is our cue we have a new paying member to WITS. When the event triggers, our listener takes in the event data and updates the customer record with the corresponding user metadata we obtained earlier. The Stripe Customer record now contains their preferred name, email, and confirmation they are a WITS member. 

Lastly, in the webhook, an additional function is called `create_hubspot_contact` which takes the Stripe customer record (first name, last name, email) and creates a Hubspot contact for them. This isn't illustrated in the diagram, but you can look at `server.py` to see how it's implemented.

Here's a diagram to illustrate how the components work:
![alt text](<DiagramWITS.jpg>)

# Future Work

+ The checkout flow currently does not have sufficient error handling. Failed payments and webhook requests should have alerts/emails sent out to wits.uwo@gmail.com. 
+ Email webhook that sends "welcome to WITS" emails to new members, containing all pertinent information to their membership
+ Clean up the repository, lot of unneccessary files are beign currently tracked that can be removed
