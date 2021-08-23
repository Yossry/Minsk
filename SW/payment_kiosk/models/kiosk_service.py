# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class KioskService(models.Model):
    _name = 'kiosk.service'
    _description = 'Kiosk Service'

    name = fields.Char(string='Service Name')
    code = fields.Char(string='Service Code')
    description = fields.Text(string='Service Description')
    service_provider_id = fields.Many2one('res.partner', string='Service Provider', domain=[('is_service_provider', '=', True)])
    rate_ids = fields.One2many('kiosk.rates', 'service_id', string='Rate Details')
    transaction_ids = fields.One2many('payment.kiosk', 'service_id', string='Transactions')
    current_month_rate = fields.Many2one('kiosk.rates', compute='_compute_current_month_rate', string='Current Month Rate')
    current_month_transaction_amount = fields.Float(compute='_compute_current_month_transaction_amount', string='Current Month Transaction Amount')
    service_product_id = fields.Many2one('product.product', string='Service Product ID', required=True)

    @api.multi
    @api.depends('transaction_ids')
    def _compute_current_month_transaction_amount(self):
        # TODO: Improved
        first_day_month = datetime.now().replace(day=1).strftime(DEFAULT_SERVER_DATE_FORMAT)
        last_day_month = datetime.now()
        last_day_month = last_day_month.replace(day=monthrange(last_day_month.year, last_day_month.month)[1])
        last_day_month = last_day_month.strftime(DEFAULT_SERVER_DATE_FORMAT)

        first_day_month = datetime.strptime(first_day_month, DEFAULT_SERVER_DATE_FORMAT)
        last_day_month = datetime.strptime(last_day_month, DEFAULT_SERVER_DATE_FORMAT)

        for service in self:
            service.current_month_transaction_amount = sum(self.transaction_ids.filtered(lambda t: t.invoice_status == 'to_invoice' and t.date >= first_day_month and t.date <= last_day_month).mapped('amount'))

    def _compute_current_month_rate(self):
        for service in self:
            service.current_month_rate = service.rate_ids.get_rate_id(service.current_month_transaction_amount)


class KioskRates(models.Model):
    _inherit = 'kiosk.rates'

    service_id = fields.Many2one('res.partner')
