# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TmsConfigSettings(models.TransientModel):
    _name = "tms.config.settings"
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.user.company_id)
    _default_expense_currency_rate = fields.Float(
        related='company_id.expense_currency_rate',
    )
