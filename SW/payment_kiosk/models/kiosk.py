# -*- coding: utf-8 -*-
from datetime import datetime
from calendar import monthrange

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PaymentKiosk(models.Model):
    _name = 'payment.kiosk'
    _rec_name = 'reference'
    _order = 'date desc, reference desc'
    _description = 'Kiosk Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    customer_name = fields.Char('Customer Name', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_lang = fields.Selection(_lang_get, 'Language', default=lambda self: self.env.lang, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_email = fields.Char('Email', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_zip = fields.Char('Zip', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_address = fields.Char('Address', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_city = fields.Char('City', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_country_id = fields.Many2one('res.country', 'Country', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    customer_phone = fields.Char('Phone', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})

    reference = fields.Char(string='Transaction Ref#', required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    naps = fields.Char(string='NAPS', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    naps_expiry = fields.Char(string='NAPS Expiry', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    aid = fields.Char(string='AID', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    sequence_no = fields.Char(string='Sequence No.', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    response_code = fields.Char(string='Response Code', required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    auth_no = fields.Char(string='Auth No.', required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    online_pin_verified = fields.Boolean(string='Online Pin Verified', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    date = fields.Datetime(string='Transaction Time', required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    amount = fields.Integer(required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    state = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Completed'),
        ('cancel', 'Canceled'),
        ('error', 'Error')],
        string='Status', default='pending', track_visibility='onchange')
    invoice_status = fields.Selection([('to_invoice', 'To Invoice'), ('invoiced', 'Invoiced')], string='Invoice Status', default='to_invoice', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    status_msg = fields.Char(string='Status Message', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    source = fields.Char(string='Transaction Source', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    merchant = fields.Char(string='Merchant Name', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    kiosk_id = fields.Many2one('kiosk.terminal', string='Kiosk Detail', required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    stn_no = fields.Char(string='STAN', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    rrn_no = fields.Char(string='RRN', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    service_id = fields.Many2one('kiosk.service', string="Service", required=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    channel_id = fields.Many2one('account.journal', string='Banking Channel', required=True, domain=[('is_kiosk_partner', '=', True)], states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    service_provider_id = fields.Many2one('res.partner', string='Service Provider', required=True,  domain=[('is_service_provider', '=', True)], states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})

    amount_payment_channel = fields.Float(compute='_compute_amount', string='Bank Charge', store=True, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    amount_service = fields.Float(compute='_compute_amount', string='Service Amount', store=True, track_visibility='onchange', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    rate_id = fields.Many2one('kiosk.rates', compute='_compute_rate', string='Rate', store=True, track_visibility='onchange', states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    posted = fields.Boolean(copy=False, states={'done': [('readonly', True)], 'error': [('readonly', True)], 'cancel': [('readonly', True)]})
    note = fields.Text(string='Description')
    move_line_ids = fields.One2many('account.move.line', 'kiosk_id', string='Journal Items')

    _sql_constraints = [
        ('reference_uniq', 'unique (reference)', 'The reference of the transaction must be unique per company !')
    ]

    @api.multi
    @api.depends('service_id')
    def _compute_rate(self):
        for payment in self:
            payment.rate_id = payment.service_id.current_month_rate.id

    @api.multi
    def _compute_service_amount(self):
        for payment in self:
            if payment.invoice_status == 'to_invoice':
                amount = (payment.amount * payment.service_id.current_month_rate.rate_percent) / 100
            else:
                amount = self.amount_service_hidden
            payment.amount_service = amount

    @api.multi
    @api.depends('amount', 'channel_id', 'service_provider_id', 'service_id', 'rate_id')
    def _compute_amount(self):
        for payment in self:
            payment.amount_payment_channel = payment.channel_id.rate_ids.get_rate(payment.amount)
            amount = (payment.amount * payment.service_id.current_month_rate.rate_percent) / 100
            payment.amount_service = min([amount, payment.service_id.current_month_rate.max_cap_amount])

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        move_vals = {
            'date': self.date,
            'ref': self.reference or '',
            'company_id': self.env.user.company_id.id,
            'journal_id': self.channel_id.id,
        }
        return move_vals

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, partner_id=False, name='', account_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': partner_id,
            'name': name,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'journal_id': self.channel_id.id,
            'account_id': account_id,
            'kiosk_id': self.id
        }

    @api.multi
    def generate_entry(self):
        aml_obj = self.env['account.move.line']
        currency_id = self.env.user.company_id.currency_id
        move = self.env['account.move'].create(self._get_move_vals())

        # account Payable
        amount = -self.amount
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date)._compute_amount_fields(
            amount, currency_id, currency_id)

        counterpart_aml_dict1 = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id,
                                                                self.service_provider_id.id, "Transaction Total on  "+self.reference,
                                                                self.service_provider_id.property_account_payable_id.id)

        # Bank Channel Account
        amount = self.amount
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date)._compute_amount_fields(amount, currency_id, currency_id)
        counterpart_aml_dict2 = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, self.service_provider_id.id, "Total Payment on " + self.reference, self.channel_id.default_debit_account_id.id)

        # Deduct From Payable (Bank Charge)
        # account Payable
        amount = self.amount_payment_channel
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date)._compute_amount_fields(
            amount, currency_id, currency_id)

        counterpart_aml_dict3 = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id,
                                                                self.service_provider_id.id, "Bank Charge (Payable) on " + self.reference,
                                                                self.service_provider_id.property_account_payable_id.id)
        # Bank Charge
        amount = -self.amount_payment_channel
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date)._compute_amount_fields(amount, currency_id, currency_id)
        counterpart_aml_dict4 = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, self.service_provider_id.id, "Bank Charge on " + self.reference, self.channel_id.default_debit_account_id.id)


        move.write({'line_ids': [(0, 0, counterpart_aml_dict4), (0, 0, counterpart_aml_dict3), (0, 0, counterpart_aml_dict2), (0, 0, counterpart_aml_dict1)]})
        move.post()
        self.write({'posted': True})
        return True

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.move_line_ids.mapped('move_id').ids)],
        }

    @api.model
    def create(self, vals):
        res = super(PaymentKiosk, self).create(vals)
        # generate entery
        res.generate_entry()

        first_day_month = datetime.now().replace(day=1).strftime(DEFAULT_SERVER_DATE_FORMAT)
        last_day_month = datetime.now()
        last_day_month = last_day_month.replace(day=monthrange(last_day_month.year, last_day_month.month)[1])
        last_day_month = last_day_month.strftime(DEFAULT_SERVER_DATE_FORMAT)

        first_day_month = datetime.strptime(first_day_month, DEFAULT_SERVER_DATE_FORMAT)
        last_day_month = datetime.strptime(last_day_month, DEFAULT_SERVER_DATE_FORMAT)
        transactions = self.search([('date', '>=', first_day_month), ('date', '<=', last_day_month), ('invoice_status', '=', 'to_invoice'), ('rate_id', '!=', res.rate_id.id)])
        transactions.write({'rate_id': res.rate_id.id})
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    kiosk_id = fields.Many2one('payment.kiosk')
