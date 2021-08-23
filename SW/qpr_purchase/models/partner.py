# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_verified = fields.Boolean()
    reference_code = fields.Char('Reference Code')

    @api.multi
    def action_verified(self):
        self.is_verified = True
