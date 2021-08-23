# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Currency(models.Model):
    _name = "res.currency"
    _inherit = "res.currency"


    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 10),
                        help='The rate of the currency to the currency of rate 1.')


class CurrencyRate(models.Model):
    _name = "res.currency.rate"
    _inherit = "res.currency.rate"

    rate = fields.Float(digits=(12, 10), default=1.0, help='The rate of the currency to the currency of rate 1')
