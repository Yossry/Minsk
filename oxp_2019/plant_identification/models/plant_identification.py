import json

from odoo import models, fields, _
from odoo.addons.iap import jsonrpc, InsufficientCreditError
from odoo.exceptions import UserError

from ..const import DEFAULT_ENDPOINT


class PlantIdentificationRequest(models.Model):
    _name = 'plant.id.request'
    _inherit = 'image.mixin'

    name = fields.Char(default='Unidentified', required=True)
    confidence = fields.Float(readonly=True)
    iap_request_id = fields.Integer(string='Request ID', help='ID of the identification request on the remote service', readonly=True)
    state = fields.Selection([('0_new', 'New'), ('1_sent', 'Sent'), ('2_identified', 'Identified')], default='0_new', readonly=True)
    results = fields.Text('Results', help='Full result of the API in JSON form for further processing, just in case.', readonly=True)

    def submit_request(self):
        user_token = self.env['iap.account'].get('plant_id')
        for request in self:
            if not request.image_1920:
                raise UserError(_('There is no picture of the plant to identify. Make sure to upload an image to be identified.'))
            params = {
                'account_token': user_token.account_token,
                'image': request.image_1920.decode('utf-8'),
            }
            # ir.config_parameter allows locally overriding the endpoint
            # for testing & al
            endpoint = self.env['ir.config_parameter'].sudo().get_param('plant_id.endpoint', DEFAULT_ENDPOINT)
            response = jsonrpc(endpoint + '/plant/v1/identify', params=params)
            request.iap_request_id = response['request_id']
            request.state = '1_sent'
        return True

    def fetch_result(self):
        user_token = self.env['iap.account'].get('plant_id')
        for request in self:
            params = {
                'account_token': user_token.account_token,
                'request_id': request.iap_request_id,
            }
            endpoint = self.env['ir.config_parameter'].sudo().get_param('plant_id.endpoint', DEFAULT_ENDPOINT)
            response = jsonrpc(endpoint + '/plant/v1/fetch', params=params)
            suggestions = response.get('suggestions', [])
            if not suggestions:
                return True
            best_guess = suggestions[0]
            request.write({
                'name': best_guess['plant']['name'],
                'confidence': best_guess['probability'],
                'results': json.dumps(response),
                'state': '2_identified',
            })