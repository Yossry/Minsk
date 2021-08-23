# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_service_provider = fields.Boolean()
    service_ids = fields.One2many('kiosk.service', 'service_provider_id', string='Services')
    transaction_ids = fields.One2many('payment.kiosk', 'service_provider_id', string='Transactions')
    provider_type = fields.Selection([('private', 'Private'), ('government', 'Government')], string='Service Provider Type')

    def _prepare_invoice_line(self):
        lines = []
        for service in self.service_ids:
            account = service.service_product_id.property_account_income_id or service.service_product_id.categ_id.property_account_income_categ_id
            if not account and service.service_product_id:
                raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                    (service.service_product_id.name, service.service_product_id.id, service.service_product_id.categ_id.name))
            amount = sum(service.transaction_ids.filtered(lambda t: t.invoice_status == 'to_invoice').mapped('amount_service'))
            if amount:
                lines.append((0, 0, {'product_id': service.service_product_id.id, 'price_unit': amount, 'quantity': 1.0, 'name': 'March Bill', 'account_id': account.id}))
        return lines

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': 'March Bill',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.property_account_receivable_id.id,
            'partner_id': self.id,
            'partner_shipping_id': self.id,
            'journal_id': journal_id,
            'company_id': self.company_id.id,
            'user_id': self.env.user.id,
            'invoice_line_ids': self._prepare_invoice_line()
        }
        return invoice_vals

    @api.multi
    def generate_bill(self):
        Invoice = self.env['account.invoice']
        for partner in self:
            if partner.transaction_ids.filtered(lambda t: t.invoice_status == 'to_invoice'):
                invoice = Invoice.create(partner._prepare_invoice())
                invoice.action_invoice_open()
                partner.transaction_ids.write({'invoice_status': 'invoiced'})
