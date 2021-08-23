# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    _sql_constraints = [
        ("unique_name_per_day", "Check(1=1)", "Remove currency rate constraint."),
    ]
