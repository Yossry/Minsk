# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class KioskTransactionReport(models.AbstractModel):
    _name = 'report.payment_kiosk.report_kiosktransaction'
    _description = 'Kiosk Transaction Summary Report'

    def _get_data(self, form):
        print("\n>>>>>>", form)
        date_from = form['date_from']
        date_to = form['date_to']
        transactions = self.env['payment.kiosk'].search([('date', '>=', date_from), ('date', '<=', date_to)])
        final_datas = {}
        for t in transactions:
            if not final_datas.get(t.service_provider_id.id):
                final_datas[t.service_provider_id.id] = {
                    'name': t.service_provider_id.name,
                    'amount': t.amount,
                    'service_amount': t.amount_service,
                    'service': {
                        t.service_id.id:
                            {
                                'name': t.service_id.name,
                                'amount': t.amount,
                                'service_amount': t.amount_service,
                                'transactions': [
                                    {
                                        'reference': t.reference,
                                        'amount': t.amount,
                                        'date': fields.Date.to_string(t.date),
                                        'stan': t.stn_no,
                                        'rrn': t.rrn_no,
                                        'service_amount': t.amount_service
                                    }
                                ]
                            },
                    }
                }
            else:
                final_datas[t.service_provider_id.id]['amount'] += t.amount
                final_datas[t.service_provider_id.id]['service_amount'] += t.amount_service
                if not final_datas[t.service_provider_id.id]['service'].get(t.service_id.id):
                    final_datas[t.service_provider_id.id]['service'][t.service_id.id] = {
                        'name': t.service_id.name,
                        'amount': t.amount,
                        'service_amount': t.amount_service,
                        'transactions': [{
                            'reference': t.reference,
                            'amount': t.amount,
                            'service_amount': t.amount_service,
                            'date': fields.Date.to_string(t.date),
                            'stan': t.stn_no,
                            'rrn': t.rrn_no,
                        }]
                    }
                else:
                    final_datas[t.service_provider_id.id]['service'][t.service_id.id]['amount'] += t.amount
                    final_datas[t.service_provider_id.id]['service'][t.service_id.id]['service_amount'] += t.amount_service
                    final_datas[t.service_provider_id.id]['service'][t.service_id.id]['transactions'].append({
                        'reference': t.reference,
                        'amount': t.amount,
                        'service_amount': t.amount_service,
                        'date': fields.Date.to_string(t.date),
                        'stan': t.stn_no,
                        'rrn': t.rrn_no,
                    })
        print("\n>>>>>>>>>", final_datas)
        return final_datas

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        kiosk_report = self.env['ir.actions.report']._get_report_from_name('payment_kiosk.report_kiosktransaction')
        transaction = self.env['payment.kiosk']
        datas = self._get_data(data.get('form'))
        print("\n>>>>>>>>", datas)
        return {
            'doc_ids': [],
            'doc_model': kiosk_report.model,
            'docs': transaction,
            'datas': datas
        }
