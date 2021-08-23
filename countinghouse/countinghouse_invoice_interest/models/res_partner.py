import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_interest_invoice(self):
        """
        Get current draft invoice for interest charges,
        or create new invoice.
        """
        self.ensure_one()
        if not self.credit and self.parent_id and not self.parent_id.credit:
            _logger.info('Not creating interest invoice. %s has no credit balance.' % self.name)
            return

        name = 'Overdue Interest'
        Invoice = self.env['account.invoice']
        invoice_contact = self.address_get(['invoice'])['invoice']

        current = Invoice.search([
            ('partner_id', '=', invoice_contact),
            ('state', '=', 'draft'),
            ('name', '=', name),
        ], limit=1, order='id desc')
        if current:
            return current

        contact = self.browse(invoice_contact)
        company = contact.company_id
        invoice = Invoice.create({
            'name': name,
            'user_id': contact.user_id.id,
            'partner_id': invoice_contact,
            'type': 'out_invoice',
            'company_id': company.id,
            'currency_id': company.currency_id.id,
        })
        invoice._onchange_partner_id()

        return invoice
