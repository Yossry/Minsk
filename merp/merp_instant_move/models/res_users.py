# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    instant_add_more = fields.Boolean(
        string='Instant Move: \'add more\' automatically',
        help='Perform \'add more\' actions automatically',
        default=False,
    )
