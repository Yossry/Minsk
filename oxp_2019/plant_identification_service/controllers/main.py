import json
import requests

from odoo.addons.iap import charge
from odoo.http import Controller, request, route
from odoo.modules.module import get_module_resource


def get_keys():
    try:
        with open(get_module_resource('plant_identification_service', 'secret_keys.json'), 'rb') as keys_file:
            keys = json.loads(keys_file.read())
    except:
        return {}
    return keys

class PlantServiceController(Controller):

    @route('/plant/v1/identify', type='json', auth='public', methods=['POST'])
    def identify(self, account_token, image, **kwargs):
        keys = get_keys()
        cost = 1
        plant_endpoint = 'https://api.plant.id/identify'
        with charge(request.env, keys['iap'], account_token, cost):
            if not keys.get('plant_id'):
                with open(get_module_resource('plant_identification_service', 'data', 'sample_response.json'), 'rb') as demo:
                    jresponse = json.loads(demo.read())['submit']
            else:
                params = {
                    'key': keys['plant_id'],
                    'images': [
                        image
                    ]
                }
                response = requests.post(plant_endpoint, json=params)
                jresponse = response.json()
            # save the remote id locally, will be needed when the customer wants to fetch the result later
            # TODO: store hash of the account_token for authentication later
            r_id = request.env['iap.plant.request'].sudo().create({'plant_request_id': jresponse.get('id')})
            jresponse['request_id'] = r_id.id
        return jresponse
    
    @route('/plant/v1/fetch', type='json', auth='public', methods=['POST'])
    def fetch(self, account_token, request_id):
        keys = get_keys()
        plant_endpoint = 'https://api.plant.id/check_identifications'
        req_id = request.env['iap.plant.request'].sudo().browse(int(request_id))
        # TODO: check account_token with stored hash on the request to be sure that the result are sent to the
        # db who made the request
        if not keys.get('plant_id'):
            with open(get_module_resource('plant_identification_service', 'data', 'sample_response.json'), 'rb') as demo:
                jresponse = json.loads(demo.read())['fetch']
        else:
            params = {
                'key': keys['plant_id'],
                'ids': [req_id.plant_request_id],
            }
            response = requests.post(plant_endpoint, json=params)
            jresponse = response.json()
        return jresponse[0]