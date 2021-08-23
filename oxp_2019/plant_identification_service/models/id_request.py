from odoo import models, fields


class IdRequest(models.Model):
    _name = 'iap.plant.request'
    _rec_name = 'id'
    
    plant_request_id = fields.Integer('ID on plant.id system')
    account_token_hash = fields.Char('Hash of the request owner token')