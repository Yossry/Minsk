from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    afex_payment_id = fields.Many2one('account.payment', string='AFEX Source', readonly=True)
    is_afex = fields.Boolean(related=['afex_payment_id', 'is_afex'], readonly=True)
    afex_ssi_details_display = fields.Html(related=['afex_payment_id', 'afex_ssi_details_display'], string='SSI Details', readonly=True)

    @api.onchange('partner_id', 'company_id', 'currency_id')
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()
        if self.type in ('in_invoice', 'out_refund') and self.partner_id and self.currency_id:
            partner_banks = self.partner_id.commercial_partner_id.bank_ids.filtered(lambda bank: bank.currency_id == self.currency_id)
            if partner_banks:
                self.partner_bank_id = partner_banks[0].id
        return result
