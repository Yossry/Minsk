# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    stock_location_id = fields.Many2one(
        'stock.location',
        string='Force Source Location for Instant Move',
        required=False,
    )

    allow_to_change_force_source_location = fields.Boolean(
        string='Allow to change Force Source Location',
    )
