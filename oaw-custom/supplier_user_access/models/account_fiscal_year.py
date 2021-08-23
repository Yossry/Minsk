# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountFiscalYear(models.Model):
    _inherit = "account.fiscal.year"

    allow_supplier_access = fields.Boolean("Allow Supplier Access", default=False)
