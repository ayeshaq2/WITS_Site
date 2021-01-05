# WITS_Site

This is the repo for the live version of the WITS website at www.wits-uwo.ca. 

.env file should never be pushed on the repo. It contains sensitive API keys that cannot be shared with malicious attackers. 

# Checkout Flow

The website uses Stripe Checkout to proces payments. All processing, authentication, and more is done on Stripe's end. All we do is redirect the user to the Stripe checkout page and back to our website. Since Stripe Checkout does not allow for custom fields, we ask the customer for their full name and email beforehand so we can update their customer record later. This is important for us as having their preferred name and email in our records allows us to integrate with Hubspot seamlessly with no manual effort.

When we create a checkout session, the user metadata is appended to Stripe Checkout data. It is propogated throughout all steps of the process. We then utilize webhooks to actively listen for whenever a checkout.session.completed event occurs, which is our cue we have a new paying member to WITS. When the event triggers, our listener takes in the event data and updates the customer record with the corresponding user metadata we obtained earlier. The Stripe Customer record now contains their preferred name, email, and confirmation they are a WITS member. 

Here's a diagram to illustrate how the components work:
![alt text](<DiagramWITS.jpg>)

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

