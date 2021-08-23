from datetime import date, timedelta
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    show_interest_btn = fields.Boolean(string='Show Interest Button',
                                       compute='show_interest_button',
                                       )
    charge_date = fields.Date(string='Last Charge Date',
                              help='Date of last interest charges'
                              )
    interest_charged = fields.Monetary(string='Interest Charged', default=0,
                                       help='Total interest charges on invoice',
                                       )

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        super(AccountInvoice, self)._onchange_payment_term_date_invoice()
        if self.type == 'out_invoice' and not self.interest_charged:
            self.charge_date = self.date_due

    def next_interest_date(self):
        if not self.charge_date:
            return self.date_invoice
        return fields.Date.from_string(self.charge_date) + timedelta(days=30)

    @api.multi
    def show_interest_button(self):
        for invoice in self:
            if invoice.state != 'open' or invoice.type != 'out_invoice':
                invoice.show_interest_btn = False
            elif invoice.residual <= 0:
                invoice.show_interest_btn = False
            elif invoice.payment_term_id and not invoice.payment_term_id.charge_interest:
                invoice.show_interest_btn = False
            elif invoice.next_interest_date() <= date.today():
                invoice.show_interest_btn = True
            else:
                invoice.show_interest_btn = False

    def interest_due(self):
        """
        Interest charges due on unpaid invoice amount.
        """
        interest_rate = self.payment_term_id.interest_rate / 100
        return round(abs((self.residual * interest_rate) / 12), self.currency_id.decimal_places)

    def get_interest_product_id(self):
        return self.with_context(
            company_id=self.company_id.id, force_company=self.company_id.id
        ).payment_term_id.product_id

    def post_interest_message(self, interest):
        """
        Post internal note on overdue invoice with the amount of interest charged.
        """
        round_dp = self.currency_id.decimal_places
        new_interest = round(interest, round_dp)
        cur_symbol = self.currency_id.symbol
        self.message_post(
            body='Added %s%s in interest charges' % (cur_symbol, new_interest)
        )

    def get_tax_ids(self):
        """
        Get tax ID mappings for invoice lines, based on product or account.
        Saves call to _onchange_product_id which resets name/price_unit
        """
        if not self.fiscal_position_id:
            return []

        if self.payment_term_id.sales_tax_policy != 'fp':
            return []

        product = self.get_interest_product_id()
        taxes = product.taxes_id or product.property_account_income_id.tax_ids
        taxes = taxes.filtered(lambda r: r.company_id == self.company_id)
        taxes = self.fiscal_position_id.map_tax(taxes, product, self.partner_id)

        return [tax.id for tax in taxes]

    def generate_interest_lines(self):
        """
        Add interest lines to invoice in 30 day increments until end of date range is
        greater than current day. Interest for each 30 day range will be calculated on
        the amount due, which will NOT be increased for each 30 day period.

        Because typical usage is assumed that this charge will be applied _every_ 30 days,
        and a new interest invoice generated each 30 day interval.

        Catchup scenarios are still supported, but "interest charges
        on the overdue interest charges" should be added to the Interest Invoice.
        """
        interest_invoice = self.partner_id.get_interest_invoice()
        if not interest_invoice:
            return

        total_interest_charged = self.interest_charged
        interest = self.interest_due()
        tax_ids = self.get_tax_ids()

        today = date.today()
        start = fields.Date.from_string(self.charge_date)
        end = self.next_interest_date()
        product_id = self.get_interest_product_id()
        interest_charged = 0
        interest_lines = []

        while end <= today:
            if interest:
                interest_charged += interest
                total_interest_charged += interest
                interest_lines.append({
                    'name': 'Invoice %s interest %s - %s' % (self.number, start, end),
                    'product_id': product_id.id,
                    'account_id': product_id.property_account_income_id.id,
                    'quantity': 1,
                    'price_unit': interest,
                    'invoice_id': self.id,
                    'company_id': self.company_id.id,
                    'invoice_line_tax_ids': [(6, 0, tax_ids)] if tax_ids else False,
                })

            start = start + timedelta(days=31)
            end = end + timedelta(days=31)

        self.write({
            'charge_date': fields.Date.to_string(start),
            'interest_charged': total_interest_charged,
        })
        if interest_lines:
            interest_invoice.write({
                'invoice_line_ids': [(0, 0, line) for line in interest_lines],
            })
        if interest_charged:
            self.post_interest_message(interest=interest_charged)

    @api.multi
    def charge_interest(self, cron=False):
        """
        Charge interest in invoice. Callable from button or cron method.
        """
        for overdue_invoice in self:

            if not overdue_invoice.show_interest_btn:
                if cron:
                    continue
                raise UserError(
                    '%s not eligible for interest charges until %s' % (
                        overdue_invoice.number,
                        fields.Date.to_string(overdue_invoice.next_interest_date())
                    )
                )

            _logger.info('Charging interest on %s' % overdue_invoice.number)
            self.generate_interest_lines()

    @api.multi
    def cron_add_interest_charges(self):
        full_interval = fields.Date.to_string(date.today() - timedelta(days=30))

        invoices = self.env['account.invoice'].search([
            ('state', '=', 'open'),
            ('type', '=', 'out_invoice'),
            ('charge_date', '<=', full_interval),
            ('payment_term_id.charge_interest', '=', True),
        ])
        for invoice in invoices:
            try:
                invoice.with_context(
                    company_id=invoice.company_id.id, force_company=invoice.company_id.id
                ).charge_interest(cron=True)
                self.env.cr.commit()
            except Exception as e:
                _logger.exception(e)
                _logger.error('Unable to charge interest on Invoice %s' % invoice.move_name)
