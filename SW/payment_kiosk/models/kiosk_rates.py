# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KioskRates(models.Model):
    _name = 'kiosk.rates'
    _description = 'Kiosk Rates'
    _order = 'sequence'

    name = fields.Char(string='Charge Name')
    sequence = fields.Integer(default=10)
    from_amount = fields.Integer(string='From Amount', required=True)
    to_amount = fields.Integer(string='To Amount', required=True)
    max_cap_amount = fields.Integer(string='Maximum Cap Amount', required=True)
    rate_percent = fields.Float(string='Rate(%)', required=True)

    @api.constrains('from_amount', 'to_amount')
    def _check_amount(self):
        for charge in self:
            if charge.from_amount > charge.to_amount:
                raise UserError(_('Minimum Amount must be less than maximum amount'))

    @api.multi
    def get_rate(self, amount):
        for r in self:
            if amount >= r.from_amount and amount <= r.to_amount:
                rate_amount = (amount * r.rate_percent) / 100
                return min([rate_amount, r.max_cap_amount])

        return 0

    @api.multi
    def get_rate_id(self, amount):
        for r in self:
            if amount >= r.from_amount and amount <= r.to_amount:
                return r
        return 0
