from odoo import api, fields, models


class User(models.Model):
    _inherit = 'res.users'

    shipbox_id = fields.Many2one('shipbox.endpoint', 'ShipBox')
