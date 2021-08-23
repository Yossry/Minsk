# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAnalyticGroup(models.Model):
    _inherit = "account.analytic.group"
    _order = "sequence"

    sequence = fields.Integer()
