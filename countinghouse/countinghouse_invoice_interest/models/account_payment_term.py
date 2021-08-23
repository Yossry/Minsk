from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    charge_interest = fields.Boolean(string='Charge Interest', default=True,
                                     help='Charge monthly interest on overdue invoices.',
                                     )
    interest_rate = fields.Float('Interest Rate', help='Annual Interest Rate')
    sales_tax_policy = fields.Selection([
        ('no', 'No Sales Tax on Interest'),
        ('fp', 'Check Invoice Fiscal Position'),
    ],
        string='Sales Tax Policy',
        default='no',
        help="""Does invoice interest qualify for sales tax?
        If so, make sure Interest product has one or more Tax IDs assigned.
        """
    )
    product_id = fields.Many2one('product.product', string='Interest Product',
                                 ondelete='restrict')

    @api.constrains('interest_rate')
    def valid_interest_rate(self):
        if not self.charge_interest:
            return

        if self.interest_rate > 100:
            raise ValidationError('Interest rate cannot exceed 100%')

        if self.interest_rate <= 0:
            raise ValidationError('Interest rate must be higher than 0%')

    @api.constrains('product_id')
    def enforce_account_id(self):
        if not self.product_id:
            return

        for company in self.env['res.company'].search([]):
            income_account = self.sudo().with_context(
                company_id=company.id, force_company=company.id
            ).product_id.property_account_income_id
            if not income_account:
                raise UserError(
                    '%s needs an Income Account configured for %s' %
                    (self.product_id.name, company.name)
                )
