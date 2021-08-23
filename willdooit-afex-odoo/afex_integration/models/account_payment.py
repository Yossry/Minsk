from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.afex_integration.models.res_company import VALUE_DATE_TYPES


RATE_DISPLAY_MESSAGE = '''
Rates provided are indicative, until a transaction is booked by the User.
'''

AFEX_TERMS_AND_COND = '''
<p>
Transactions are powered and provided by
<a target="_blank" href="https://www.afex.com/bstc.php">AFEX</a>.
&ldquo;AFEX&rdquo; is the marketing trade name for the International Payment
Solutions and Risk Management Solutions provided by the AFEX group of related
companies, including parents, subsidiaries, and affiliated entities. Use of
this service is governed by the AFEX Terms and Conditions accepted by the
Client.
</p>
'''

AFEX_TRADE_TERMS = '''
<br/>
<p>
You acknowledge that by clicking on VALIDATE you have agreed to execute the
transaction. Use of this service is governed by AFEX’s Terms and Conditions
accepted by the Client. A confirmation of the transaction will be sent to you
by AFEX.
</p>
<img src='/afex_integration/static/image/afex_logo.png'/>
<p>
Transactions are powered and provided by
<a target="_blank" href="https://www.afex.com/bstc.php">AFEX</a>.
&ldquo;AFEX&rdquo; is the marketing trade name for the International Payment
Solutions and Risk Management Solutions provided by the AFEX group of related
companies, including parents, subsidiaries, and affiliated entities. Use of
this service is governed by the AFEX Terms and Conditions accepted by the
Client.
</p>
'''

AFEX_DATE_FORMAT = '%Y/%m/%d'
AFEX_FUNDING_BALANCE_RETRIEVED_EXPIRY = 120 # In seconds


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    is_afex = fields.Boolean(
        related=['journal_id', 'afex_journal'], readonly=True)
    afex_quote_id = fields.Integer(copy=False)
    afex_trade_no = fields.Char(string="AFEX Trade#", copy=False)
    afex_rate = fields.Float()
    afex_rate_display = fields.Html(
        string="AFEX Rate", compute='_afex_rate_display')
    afex_terms_display = fields.Html(
        compute='_afex_terms_display')
    afex_allow_earliest_value_date = fields.Boolean(
        string="Allow Earliest Value Date", copy=False)
    afex_value_date_type = fields.Selection(
        selection=VALUE_DATE_TYPES, string="Payment Type",
        default='SPOT', copy=False,
        help=("Choose between 'Today', 'Next business day' or "
              "'Two business days' rate for your trade request."))
    afex_value_date_type_old = fields.Selection(
        selection=VALUE_DATE_TYPES,
        copy=False)

    afex_stl_currency_id = fields.Many2one('res.currency')
    afex_stl_amount = fields.Monetary(
        string='Settlement Amount', currency_field='afex_stl_currency_id')

    has_afex_fees = fields.Boolean(
        compute='_compute_has_afex_fees'
        )
    afex_fee_amount_ids = fields.One2many(
        'account.payment.afex.fee', 'payment_id',
        string='AFEX Fee(s)')

    passed_currency_id = fields.Many2one(
        'res.currency')

    afex_direct_debit = fields.Boolean(
        string='Direct Debit', default=False, copy=False,
        help="Enable this if you want direct debit settlement option.")
    afex_direct_debit_journal_id = fields.Many2one(
        related='journal_id.afex_direct_debit_journal_id',
        readonly=True)

    # AFEX Scheduled Payment
    afex_scheduled_payment = fields.Boolean(
        related='journal_id.afex_scheduled_payment', readonly=True)
    afex_funding_balance = fields.Monetary(
        string='Balance', readonly=True, currency_field='afex_stl_currency_id',
        help="Total Un-cleared Fund that made up until today's value date")
    afex_funding_balance_available = fields.Monetary(
        string='Available Balance', readonly=True,
        currency_field='afex_stl_currency_id',
        help="Total Available Cleared Funds up to today's value date")
    afex_funding_balance_retrieved_date = fields.Datetime(
        string='Funding Balance Retrieved Date', copy=False)
    afex_reference_no = fields.Char(string="AFEX Reference Nr.", copy=False,
        help="Reference number retrieved from scheduled payment")

    afex_purpose_of_payment_id = fields.Many2one(
        'afex.purpose.of.payment',
        string="Purpose of Payment",
        copy=False)
    afex_purpose_of_payment = fields.Char(
        string="Remittance",
        size=35,
        copy=False)
    partner_country_id = fields.Many2one(
        related='partner_id.country_id',
        readonly=True,
        store=True)
    afex_bank_country_id = fields.Many2one(
        'res.country',
        compute='_compute_afex_bank_country_id',
        string="AFEX Bank Country",
        readonly=True,
        store=True)

    @api.depends('is_afex', 'partner_id', 'currency_id')
    def _compute_afex_bank_country_id(self):
        for payment in self.filtered(lambda p: p.is_afex and p.currency_id
                                     and p.partner_id):
            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            payment.afex_bank_country_id = afex_bank.afex_bank_country_id.id

    @api.onchange('journal_id')
    def _onchange_journal_extra(self):
        self.afex_direct_debit = self.journal_id.afex_direct_debit
        self.afex_value_date_type = \
            self.journal_id.company_id.afex_value_date_type
        self.afex_allow_earliest_value_date = \
            self.journal_id.company_id.afex_allow_earliest_value_date

    @api.onchange('amount', 'currency_id', 'journal_id')
    def _onchange_afex(self):
        self.afex_quote_id = False
        self.afex_stl_amount = 0
        self.afex_fee_amount_ids = False
        self.afex_funding_balance_retrieved_date = False

    @api.onchange('journal_id', 'currency_id', 'afex_value_date_type')
    def _onchange_scheduled_payment_date(self):
        today = fields.Date.context_today(self)
        payment_date = today
        warning = {}
        if self.is_afex:
            if self.afex_scheduled_payment and self.invoice_ids:
                due_dates = self.invoice_ids.mapped('date_due')
                payment_date = due_dates and max(min(due_dates), today) or \
                    False
                self.afex_value_date_type_old = False
            elif not self.afex_scheduled_payment and self.afex_value_date_type:
                stl_currency = self.journal_id.currency_id or \
                    self.journal_id.company_id.currency_id
                currencypair = "%s%s" % (
                    self.currency_id.name, stl_currency.name)

                url = "valuedates?currencypair=%s&valuetype=%s" \
                    % (currencypair, self.afex_value_date_type)
                response_json = self.env['afex.connector'].afex_response(
                        url, payment=self)
                if response_json.get('ERROR', True):
                    # If value date is not available for the currency, return
                    #   a warning and set the payment type and payment date
                    #   back to original
                    warning['title'] = _("Error with Payment Type")
                    message = "%s Please choose a different Payment Type."
                    message = message % response_json.get('message', "")
                    warning['message'] = _(message)
                    self.afex_allow_earliest_value_date = True
                    self.afex_value_date_type = self.afex_value_date_type_old
                    payment_date = self.payment_date or today
                else:
                    self.afex_value_date_type_old = self.afex_value_date_type
                    value_date = response_json.get('items')
                    if value_date:
                        payment_date = datetime.strptime(
                            value_date, AFEX_DATE_FORMAT)
                        payment_date = fields.Date.to_string(payment_date)
        self.payment_date = payment_date
        return {'warning': warning}

    @api.onchange('is_afex', 'partner_id', 'currency_id')
    def onchange_purpose_of_payment(self):
        self.afex_purpose_of_payment_id = False
        if (self.is_afex and self.afex_bank_country_id and self.currency_id
                and self.partner_country_id):
            # Get purpose of payments
            url = ('purposeOfPayment?BankCountryCode=%s&Currency=%s'
                   '&BeneficiaryCountryCode=%s&HighValue=TRUE'
                   % (self.afex_bank_country_id.code, self.currency_id.name,
                      self.partner_country_id.code)
                   )
            response_json = self.env['afex.connector'].afex_response(
                url)
            if response_json.get('ERROR', True):
                raise UserError(
                    _("Error while getting purpose of payment: %s") %
                      (response_json.get('message', ''))
                )

            # Create/activate purpose of payments retrieved
            Purpose = self.env['afex.purpose.of.payment']
            purposes = Purpose.search([
                ('afex_bank_country_id', '=', self.afex_bank_country_id.id),
                ('currency_id', '=', self.currency_id.id),
                ('partner_country_id', '=', self.partner_country_id.id),
                ('active', 'in', [False, True]),
                ])
            purposes_retrieved = Purpose
            for result in response_json.get('items', []):
                # Checked if purpose of payment code is already existing for
                #   bank country, partner country and currency. If not create
                #   new purpose of payment.
                purpose = purposes.filtered(lambda p: p.code==result['Code'])
                if not purpose:
                    purpose = Purpose.create(
                        {'name': result['Description'],
                         'code': result['Code'],
                         'afex_bank_country_id': self.afex_bank_country_id.id,
                         'currency_id': self.currency_id.id,
                         'partner_country_id': self.partner_country_id.id,
                         })
                elif purpose and not purpose.active:
                    purpose.write({'active': True})
                purposes_retrieved |= purpose

            # Deactivate purpose of payments that are not retrieved
            (purposes - purposes_retrieved).write({'active': False})

    @api.depends('afex_fee_amount_ids')
    @api.multi
    def _compute_has_afex_fees(self):
        for payment in self:
            payment.has_afex_fees = payment.afex_fee_amount_ids

    @api.depends('afex_quote_id')
    @api.multi
    def _afex_rate_display(self):
        for payment in self:
            if payment.afex_quote_id and payment.afex_rate:
                payment.afex_rate_display = \
                    '<p>Exchange Rate: %s to %s: %s</p>' \
                    '<p>%s</p>' %\
                    (payment.afex_stl_currency_id.name,
                     payment.currency_id.name,
                     payment.afex_rate,
                     RATE_DISPLAY_MESSAGE,
                     )
            else:
                payment.afex_rate_display = ''

    @api.depends('is_afex')
    @api.multi
    def _afex_terms_display(self):
        for payment in self:
            if payment.is_afex:
                payment.afex_terms_display = AFEX_TRADE_TERMS
            else:
                payment.afex_terms_display = ''

    @api.multi
    def refresh_quote(self):
        self.ensure_one()
        self.afex_check()
        self.request_afex_quote()
        self.retrieve_afex_balance()
        if not self.env.context.get('not_wizard'):
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'res_id': self.id,
                'view_id': self.env.ref('account.view_account_payment_invoice_form').id,
                'target': 'new',
                'context': self.env.context,
            }

    @api.multi
    def request_afex_quote(self):
        self.ensure_one()
        payment = self.filtered(lambda p: not p.afex_scheduled_payment)

        Connector = self.env['afex.connector']
        if payment.is_afex:
            if payment.multi:
                raise UserError(
                    _('AFEX payment can only be made if a single vendor or '
                      'vendor bank account is being paid'))
            if (payment.afex_direct_debit
                    and not payment.afex_direct_debit_journal_id.bank_account_id.acc_number):
                raise UserError(
                    _('Direct Debit Journal has no bank account'))

            stl_currency = payment.journal_id.currency_id or \
                payment.journal_id.company_id.currency_id
            currencypair = "%s%s" % (
                payment.currency_id.name, stl_currency.name)

            url = "valuedates?currencypair=%s&valuetype=%s" \
                % (currencypair, self.afex_value_date_type)
            response_json = Connector.afex_response(
                    url, payment=payment)
            if response_json.get('ERROR', True):
                raise UserError(
                    _("Error with Payment Type: %s Please"
                      " choose a different Payment Type.") %
                    (response_json.get('message', ''),))
            valuedate = response_json.get('items', fields.Date.context_today(self))

            url = "quote?currencypair=%s&valuedate=%s" \
                % (currencypair, valuedate)
            response_json = Connector.afex_response(
                url, payment=payment)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error with quote: %s') %
                    (response_json.get('message', ''),))

            afex_quote_id = response_json.get('QuoteId')
            afex_terms = response_json.get('Terms')
            afex_rate = response_json.get('Rate')
            if afex_terms == 'A' and afex_rate:
                afex_rate = 1.0 / afex_rate

            if not afex_quote_id or not afex_rate:
                raise UserError(_('Could not retrieve a valid AFEX quote'))
            payment_amount = stl_currency.round(payment.amount / afex_rate)

            url = "fees"
            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            account_number = payment.afex_direct_debit and \
                payment.afex_direct_debit_journal_id.bank_account_id.acc_number or \
                ''
            data = {"Amount": payment.amount,
                    "AccountNumber": account_number,
                    "SettlementCcy": stl_currency.name,
                    "TradeCcy": payment.currency_id.name,
                    "VendorId": afex_bank.afex_unique_id,
                    "ValueDate": valuedate,
                    }
            response_json = Connector.afex_response(
                url, data=data, payment=payment, post=True)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error while retrieving AFEX Fees: %s') %
                    (response_json.get('message', ''),))

            afex_fee_amount_ids = [(5, 0, 0)]
            for fee_details in response_json.get('items', []):
                fee_amount = fee_details.get('Amount')
                afex_fee_currency = \
                    self.env['res.currency'].search(
                        [('name', '=', fee_details.get('Currency', ''))],
                        limit=1)
                afex_fee_amount_ids.append((0, 0, {
                    'afex_fee_amount': fee_amount,
                    'afex_fee_currency_id': afex_fee_currency.id,
                    }))

            payment.write({'afex_quote_id': afex_quote_id,
                           'afex_rate': afex_rate,
                           'afex_stl_currency_id': stl_currency.id,
                           'afex_stl_amount': payment_amount,
                           'afex_fee_amount_ids': afex_fee_amount_ids,
                           'payment_date': valuedate,
                           })

    @api.multi
    def retrieve_afex_balance(self):
        self.ensure_one()
        payment = self.filtered(lambda p: p.afex_scheduled_payment)

        Connector = self.env['afex.connector']
        if payment.is_afex:
            if payment.multi:
                raise UserError(
                    _('AFEX payment can only be made if a single vendor or '
                      'vendor bank account is being paid'))

            payment_date = fields.Date.from_string(payment.payment_date)
            if payment_date.weekday() >= 5:
                raise UserError(
                    _('The payment date is not a valid business day.')
                    )

            stl_currency = payment.journal_id.currency_id or \
                payment.journal_id.company_id.currency_id

            if stl_currency != payment.currency_id:
                raise UserError(
                    _('Wrong payment currency selected'))

            url = "fees"
            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            data = {"Amount": payment.amount,
                    "SettlementCcy": stl_currency.name,
                    "TradeCcy": payment.currency_id.name,
                    "VendorId": afex_bank.afex_unique_id,
                    "ValueDate": payment_date.strftime(AFEX_DATE_FORMAT),
                    }
            response_json = Connector.afex_response(
                url, data=data, payment=payment, post=True)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error while retrieving AFEX Fees: %s') %
                    (response_json.get('message', ''),))

            afex_fee_amount_ids = [(5, 0, 0)]
            for fee_details in response_json.get('items', []):
                fee_amount = fee_details.get('Amount')
                afex_fee_currency = \
                    self.env['res.currency'].search(
                        [('name', '=', fee_details.get('Currency', ''))],
                        limit=1)
                afex_fee_amount_ids.append((0, 0, {
                    'afex_fee_amount': fee_amount,
                    'afex_fee_currency_id': afex_fee_currency.id,
                    }))

            afex_funding_balance = 0.0
            afex_funding_balance_available = 0.0
            url = "funding"
            response_json = Connector.afex_response(
                url)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error while retrieving AFEX Funding Balance: %s') %
                    (response_json.get('message', ''),))
            for funding_details in response_json.get('items', []):
                if stl_currency.name == funding_details.get('Currency'):
                    afex_funding_balance = funding_details.get('Balance')
                    afex_funding_balance_available = \
                        funding_details.get('AvailableBalance')
                    break

            payment.write({'afex_stl_currency_id': stl_currency.id,
                           'afex_stl_amount': 0.0,
                           'afex_fee_amount_ids': afex_fee_amount_ids,
                           'afex_funding_balance': afex_funding_balance,
                           'afex_funding_balance_available': \
                                afex_funding_balance_available,
                           'afex_funding_balance_retrieved_date': \
                                fields.Datetime.now(),
                           })

    @api.multi
    def afex_check(self):
        for payment in self.filtered(lambda p: p.is_afex):
            if payment.multi:
                raise UserError(
                    _('AFEX payment can only be made if a single vendor or '
                      'vendor bank account is being paid'))

            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            if not afex_bank.afex_unique_id:
                raise UserError(
                    _('Partner [%s] currency [%s] has not been synced with '
                      'AFEX') % (payment.partner_id.name,
                                 payment.currency_id.name))
            if payment.partner_id.afex_sync_status != 'done' or\
                    afex_bank.afex_sync_status != 'done':
                raise UserError(
                    _('Partner [%s] needs to be resynced with AFEX.') %
                    (payment.partner_id.name,)
                    )


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.model
    def default_get(self, fields):
        rec = super(AccountRegisterPayments, self).default_get(fields)
        rec.update({'passed_currency_id': rec['currency_id']})
        return rec

    afex_fee_amount_ids = fields.One2many(
        'account.payment.afex.fee', 'register_payment_id',
        string='AFEX Fee(s)')

    @api.onchange('is_afex')
    def onchange_is_afex(self):
        if self.is_afex:
            self.group_invoices = True

    @api.multi
    def refresh_quote(self):
        self.ensure_one()
        self.afex_check()
        self.request_afex_quote()
        self.retrieve_afex_balance()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.register.payments',
            'res_id': self.id,
            'view_id': self.env.ref('account.view_account_payment_from_invoices').id,
            'target': 'new',
            'context': self.env.context,
        }

    def _prepare_payment_vals(self, invoices):
        result = super(
            AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        result.update({
            'afex_quote_id': self.afex_quote_id,
            'afex_rate': self.afex_rate,
            'afex_stl_currency_id': self.afex_stl_currency_id.id,
            'afex_stl_amount': self.afex_stl_amount,
            'afex_fee_amount_ids': [(6, 0, self.afex_fee_amount_ids.ids)],
            'afex_direct_debit': self.afex_direct_debit,
            'afex_funding_balance': self.afex_funding_balance,
            'afex_funding_balance_available': \
                self.afex_funding_balance_available,
            'afex_funding_balance_retrieved_date': \
                self.afex_funding_balance_retrieved_date,
            'afex_reference_no': self.afex_reference_no,
            'afex_purpose_of_payment_id': self.afex_purpose_of_payment_id.id,
            'afex_purpose_of_payment': self.afex_purpose_of_payment,
            })
        return result


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        rec.update({'passed_currency_id': rec.get('currency_id', False)})
        return rec

    afex_invoice_ids = fields.One2many(
        'account.invoice', 'afex_payment_id')
    afex_stl_invoice_id = fields.Many2one(
        'account.invoice',
        string='AFEX Invoice', readonly=True)
    afex_fee_invoice_ids = fields.One2many(
        'account.invoice',
        string='AFEX Fee Invoice(s)',
        compute='_compute_fee_invoices',
        )

    afex_ssi_account_number = fields.Char(copy=False)
    afex_ssi_details = fields.Html(copy=False)
    afex_ssi_details_display = fields.Html(
        compute="afex_ssi", string="SSI Details")

    @api.onchange('partner_id')
    def _onchange_afex_partner(self):
        self._onchange_afex()

    @api.one
    def _compute_fee_invoices(self):
        self.afex_fee_invoice_ids =\
            self.afex_invoice_ids - self.afex_stl_invoice_id

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        self.afex_check()
        self.create_afex_trade()
        self.create_afex_scheduled_payment()
        return res

    def create_afex_trade(self):
        for payment in self.filtered(lambda p: p.is_afex
                                     and not p.afex_scheduled_payment):
            if not payment.afex_rate or \
                    not payment.afex_quote_id or \
                    payment.afex_quote_id < 1:
                raise UserError(
                    _('Invalid AFEX Quote - Please re-quote before attempting'
                      ' payment.'))

            if payment.partner_id.afex_sync_status != 'done':
                raise UserError(
                    _('Partner needs to be resynced with AFEX before a trade'
                      ' can be made.')
                    )

            inv_head = self.env['account.invoice'].with_context(
                type='in_invoice').create(
                {'partner_id': payment.journal_id.afex_partner_id.id,
                 'user_id': self.env.user.id,
                 'company_id': payment.company_id.id,
                 'currency_id': payment.afex_stl_currency_id.id,
                 })
            inv_head._onchange_partner_id()
            inv_head.date_invoice = inv_head.date_due =\
                fields.Date.context_today(self)
            inv_head._onchange_payment_term_date_invoice()
            self.env['account.invoice.line'].create(
                {'invoice_id': inv_head.id,
                 'account_id': payment.journal_id.default_debit_account_id.id,
                 'name': 'AFEX Settlement',
                 'price_unit': payment.afex_stl_amount,
                 'quantity': 1,
                 })

            invoices = {
                payment.afex_stl_currency_id.id: inv_head
                }
            for fee in payment.afex_fee_amount_ids:
                if fee.afex_fee_currency_id.id in invoices:
                    inv_fee = invoices[fee.afex_fee_currency_id.id]
                else:
                    inv_fee = self.env['account.invoice'].with_context(
                        type='in_invoice').create(
                        {'partner_id': payment.journal_id.afex_partner_id.id,
                         'user_id': self.env.user.id,
                         'company_id': payment.company_id.id,
                         'currency_id': fee.afex_fee_currency_id.id,
                         })
                    inv_fee._onchange_partner_id()
                    inv_fee.date_invoice = inv_fee.date_due =\
                        fields.Date.context_today(self)
                    invoices[fee.afex_fee_currency_id.id] = inv_fee
                self.env['account.invoice.line'].create(
                    {'invoice_id': inv_fee.id,
                     'account_id': payment.journal_id.afex_fee_account_id.id,
                     'name': 'AFEX Transaction Fee',
                     'price_unit': fee.afex_fee_amount,
                     'quantity': 1,
                     })

            url = "trades/create"
            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            account_number = payment.afex_direct_debit and \
                payment.afex_direct_debit_journal_id.bank_account_id.acc_number or \
                ''
            payment_date = fields.Date.from_string(payment.payment_date)
            data = {"Amount": payment.amount,
                    "AccountNumber": account_number,
                    "TradeCcy": payment.currency_id.name,
                    "SettlementCcy": payment.afex_stl_currency_id.name,
                    "QuoteId": payment.afex_quote_id,
                    "VendorId": afex_bank.afex_unique_id,
                    "PurposeOfPayment": payment.afex_purpose_of_payment or '',
                    "ValueDate": payment_date.strftime(AFEX_DATE_FORMAT),
                    }
            if payment.afex_purpose_of_payment_id:
                data["POPCode"] = payment.afex_purpose_of_payment_id.code
            response_json = self.env['afex.connector'].afex_response(
                url, data=data, payment=payment, post=True)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error while creating AFEX Trade: %s') %
                    (response_json.get('message', ''),))
            trade_number = response_json.get('TradeNumber', False)
            if trade_number:
                ssi_account_number = payment.company_id.afex_api_key and \
                    len(payment.company_id.afex_api_key) > 8 and \
                    payment.company_id.afex_api_key[0:8] or ''
                payment.afex_trade_no = trade_number
                payment.afex_ssi_account_number = ssi_account_number

                ssi_details = []

                instruction_currencies = payment.afex_stl_currency_id\
                        | payment.afex_fee_amount_ids.mapped(
                            'afex_fee_currency_id')
                if payment.afex_direct_debit:
                    instruction_currencies -= payment.afex_stl_currency_id
                    ssi_details.append(
                        "<strong>Instructions for %s Amount:</strong>"
                        "<br/>Settlement for this was by direct debit" %
                        (payment.afex_stl_currency_id.name)
                        )

                for currency in instruction_currencies:
                    url = "ssi/GetSSI?Currency=%s" % (
                        currency.name,)

                    response_json = self.env['afex.connector'].afex_response(
                        url)
                    if not response_json.get('ERROR', True):
                        instructions = [
                            x['PaymentInstructions']
                            for x in response_json.get('items', [])
                            if x.get('PaymentInstructions')]
                        if instructions:
                            ssi_details.append(
                                '<strong>Instructions for %s Amount:</strong>'
                                '<br/>%s' %
                                (currency.name,
                                    '<br/>'.join(instructions).replace(
                                        '\r', '<br/>'
                                        )
                                 )
                                )

                afex_ssi_details = "<br/>".join(ssi_details)
                if instruction_currencies:
                    afex_ssi_details += (
                        "<p><strong>Please remember to include the AFEX"
                        " Account Number <%s> in remittance information."
                        "</strong></p>" % (ssi_account_number)
                        )
                else:
                    afex_ssi_details += "<p/>"
                payment.afex_ssi_details = afex_ssi_details

                for invoice in invoices.values():
                    if invoice == inv_head:
                        invoice.reference = '%s %s' % (
                            ssi_account_number,
                            trade_number
                            )
                    else:
                        invoice.reference = 'Fee[%s] %s %s' % (
                            invoice.currency_id.name,
                            ssi_account_number,
                            trade_number
                            )

                for invoice in invoices.values():
                    invoice.action_invoice_open()

            payment.write({
                'afex_invoice_ids': [
                    (6, 0,
                     [i.id for i in invoices.values()]
                     )],
                'afex_stl_invoice_id': inv_head.id,
                })

            dd_journal_currency = payment.afex_direct_debit_journal_id.currency_id or \
                payment.afex_direct_debit_journal_id.company_id.currency_id
            if (payment.afex_direct_debit
                    and payment.afex_stl_invoice_id.currency_id == dd_journal_currency):
                if payment.afex_stl_invoice_id.state == 'draft':
                    payment.afex_stl_invoice_id.action_invoice_open()
                payment_methods = payment.afex_direct_debit_journal_id.outbound_payment_method_ids
                self.env['account.payment'].with_context(
                    active_ids=payment.afex_stl_invoice_id.ids,
                    default_invoice_ids=[(4, payment.afex_stl_invoice_id.id)],
                    default_journal_id=payment.afex_direct_debit_journal_id,
                    default_payment_method_id = payment_methods and payment_methods[0].id,
                    ).create({}).post()

    def create_afex_scheduled_payment(self):
        for payment in self.filtered(lambda p: p.is_afex
                                     and p.afex_scheduled_payment):
            retrieved_date = payment.afex_funding_balance_retrieved_date
            retrieved_allow_date = retrieved_date and \
                fields.Datetime.from_string(retrieved_date) + \
                timedelta(seconds=AFEX_FUNDING_BALANCE_RETRIEVED_EXPIRY)
            now = fields.Datetime.from_string(fields.Datetime.now())
            if not retrieved_allow_date or retrieved_allow_date < now:
                raise UserError(
                    _('Invalid AFEX Funding Balance Retrieval - Please '
                      'retrieve balance again before attempting  payment.'))
            if payment.partner_id.afex_sync_status != 'done':
                raise UserError(
                    _('Partner needs to be resynced with AFEX before a'
                      ' funding balance retrieval.')
                    )

            payment_date = fields.Date.from_string(payment.payment_date)
            if payment_date.weekday() >= 5:
                raise UserError(
                    _('The payment date is not a valid business day.')
                    )

            invoices = {}
            for fee in payment.afex_fee_amount_ids:
                if fee.afex_fee_currency_id.id in invoices:
                    inv_fee = invoices[fee.afex_fee_currency_id.id]
                else:
                    inv_fee = self.env['account.invoice'].with_context(
                        type='in_invoice').create(
                        {'partner_id': payment.journal_id.afex_partner_id.id,
                         'user_id': self.env.user.id,
                         'company_id': payment.company_id.id,
                         'currency_id': fee.afex_fee_currency_id.id,
                         })
                    inv_fee._onchange_partner_id()
                    inv_fee.date_invoice = inv_fee.date_due =\
                        fields.Date.context_today(self)
                    invoices[fee.afex_fee_currency_id.id] = inv_fee
                self.env['account.invoice.line'].create(
                    {'invoice_id': inv_fee.id,
                     'account_id': payment.journal_id.afex_fee_account_id.id,
                     'name': 'AFEX Transaction Fee',
                     'price_unit': fee.afex_fee_amount,
                     'quantity': 1,
                     })

            url = "Payments/Create"
            afex_bank = payment.partner_id.afex_bank_for_currency(
                payment.currency_id)
            data = {"Currency": payment.currency_id.name,
                    "VendorId": afex_bank.afex_unique_id,
                    "Amount": payment.amount,
                    "PaymentDate": payment_date.strftime(AFEX_DATE_FORMAT),
                    "PurposeOfPayment": payment.afex_purpose_of_payment or '',
                    }
            if payment.afex_purpose_of_payment_id:
                data["POPCode"] = payment.afex_purpose_of_payment_id.code
            response_json = self.env['afex.connector'].afex_response(
                url, data=data, payment=payment, post=True)
            if response_json.get('ERROR', True):
                raise UserError(
                    _('Error while creating AFEX Scheduled Payment: %s') %
                    (response_json.get('message', ''),))
            reference_number = response_json.get('ReferenceNumber', False)
            if reference_number:
                ssi_account_number = payment.company_id.afex_api_key and \
                    len(payment.company_id.afex_api_key) > 8 and \
                    payment.company_id.afex_api_key[0:8] or ''
                payment.afex_reference_no = reference_number
                payment.afex_ssi_account_number = ssi_account_number

                ssi_details = []
                for currency in payment.afex_fee_amount_ids.mapped(
                        'afex_fee_currency_id'):
                    url = "ssi/GetSSI?Currency=%s" % (
                        currency.name,)

                    response_json = self.env['afex.connector'].afex_response(
                        url)
                    if not response_json.get('ERROR', True):
                        instructions = [
                            x['PaymentInstructions']
                            for x in response_json.get('items', [])
                            if x.get('PaymentInstructions')]
                        if instructions:
                            ssi_details.append(
                                '<strong>Instructions for %s Amount:</strong>'
                                '<br/>%s' %
                                (currency.name,
                                    '<br/>'.join(instructions).replace(
                                        '\r', '<br/>'
                                        )
                                 )
                                )

                payment.afex_ssi_details = \
                    "%s<p><strong>Please remember to include the AFEX Account"\
                    " Number <%s> in remittance information.</strong></p>" % \
                    ('<br/>'.join(ssi_details),
                     ssi_account_number
                     )

                for invoice in invoices.values():
                    invoice.reference = 'Fee[%s] %s %s' % (
                        invoice.currency_id.name,
                        ssi_account_number,
                        reference_number
                        )

                for invoice in invoices.values():
                    invoice.action_invoice_open()

            payment.write({
                'afex_invoice_ids': [
                    (6, 0,
                     [i.id for i in invoices.values()]
                     )],
                })

    def afex_ssi(self):
        for payment in self:
            if not payment.afex_ssi_details:
                payment.afex_ssi_details_display = False
            else:
                payment_amounts = '<br/>'
                payment_amounts = '%s<p>Payment Amount (%s): %.2f</p>' %\
                    (payment_amounts,
                     payment.currency_id.name,
                     payment.amount,
                     )
                if not payment.afex_scheduled_payment:
                    payment_amounts = '%s<p>Settlement Amount (%s): %.2f</p>' %\
                        (payment_amounts,
                         payment.afex_stl_currency_id.name,
                         payment.afex_stl_amount,
                         )
                for fee in payment.afex_fee_amount_ids:
                    payment_amounts = '%s<p>Fee Amount (%s): %.2f</p>' %\
                        (payment_amounts,
                         fee.afex_fee_currency_id.name,
                         fee.afex_fee_amount,
                         )
                payment.afex_ssi_details_display = \
                    " ".join(
                        [payment_amounts,
                         payment.afex_ssi_details,
                         "<img src='/afex_integration/static/image/"
                         "afex_logo.png'/><br/>",
                         AFEX_TERMS_AND_COND])


class AccountPaymentAfexFee(models.Model):
    _name = 'account.payment.afex.fee'
    _description = 'Account Payment Afex Fee'

    payment_id = fields.Many2one(
        'account.payment', ondelete='cascade')
    register_payment_id = fields.Integer(
        help=("ID reference for account.register.payments"
              " since TransientModel cannot be linked"))
    afex_fee_amount = fields.Monetary(
        string='AFEX Fee Amount', currency_field='afex_fee_currency_id')
    afex_fee_currency_id = fields.Many2one(
        'res.currency', string='Fee Currency')
