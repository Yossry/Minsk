# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KioskTransactionReportWizard(models.TransientModel):

    _name = 'kiosk.transaction.report.wizard'
    _description = 'Kiosk Transaction Report Wizard'

    date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='To', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    service_provider_ids = fields.Many2many('res.partner', string='Service Providers', domain=[('is_service_provider', '=', True)])

    @api.multi
    def print_report(self):
        self.ensure_one()
        print("\n>>>>>herere")
        [data] = self.read()
        if not data.get('service_provider_ids'):
            raise UserError(_('You have to select at least one Service Provider.'))
        datas = {
            'ids': [],
            'model': 'payment.kiosk',
            'form': data
        }
        return self.env.ref('payment_kiosk.action_report_kiosktransaction').with_context(from_transient_model=True).report_action(self.env['payment.kiosk'], data=datas)
