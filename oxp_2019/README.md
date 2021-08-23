# IAP Demo Code

This repository contains the demo for the talk/tutorial about developping
In-App Purchase (IAP) services for Odoo apps.

It is made up of 2 modules:
- `plant_identification_service`: the service module, which should run on your server
- `plant_identification`: the client module, which will run on the customer's instance

# Guide

## IAP Sandbox

You should first register the service on the IAP Sandbox. In this case, the service key (which is unique) is `plant_id` - if you want to run this code locally, you will need to change it. Once registered, you will obtain the service key used to charge your customer for IAP services. It should be stored somewhere and not committed to your CVS. In this case, the key is stored at the root of the `plant_identification_service` module as a json file, along with the API key for the plant identification service used for this demo (https://plant.id).

## `plant_identification_service`

This module should run in its own instance somewhere accessible over http by the client module (default: `http://localhost:8099`, configurable in the `const.py` file of the client module). Simply install the module; for demo purposes you should also ensure that the `iap.endpoint` is set to the IAP sandbox:
```sql
INSERT INTO ir_config_parameter (key, value) VALUES ('iap.endpoint', 'https://iap-sandbox.odoo.com');
```

(this can also be done through Odoo's UI).

## `plant_identification`

This module will be installed by customer and should be made available easily (e.g. the Odoo Apps Store). The same switch should be done for the IAP server endpoint so that it contacts the sandbox by default:
```sql
INSERT INTO ir_config_parameter (key, value) VALUES ('iap.endpoint', 'https://iap-sandbox.odoo.com');
```
This modules contains a `const.py` file which contains the URL of the IAP service.


## Using the service
In the customer database, with the client module installed, create a new request. Upload a photo of your plant and submit the request. You will get an 'Insufficient Credit' error on the first try - follow the link to credit your account (since this is a sandbox service, adding credit is free and done in one click). You should then be able to process the request.

# About plant.id

[Plant.id](https://plant.id) is an API that allows you to identify plants based on a single (or multiple) pictures as well as other metadata (e.g. geographic coordinates, etc. - though this demo only uses a single image to keep things simple).

They agreed to provide me with an API key for the purpose of this demo. Obviously, you should *not* contact them do to the same unless you intent to use the service for real.

If no API key is found for the service in the `secret_keys.json` file, a default response will be provided instead, allowing you to test the addons without an API key.
