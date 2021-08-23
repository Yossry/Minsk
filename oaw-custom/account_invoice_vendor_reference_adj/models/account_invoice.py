# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _check_duplicate_supplier_reference(self):
        # QTL EDIT: Skip Checking on duplicated vendor bill reference
        # for invoice in self:
        #     # refuse to validate a vendor bill/credit note if there already exists one with the same reference for the same partner, # noqa
        #     # because it's probably a double encoding of the same bill/credit note # noqa
        #     if invoice.type in ('in_invoice', 'in_refund') and invoice.reference: # noqa
        #         if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]): # noqa
        #             raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note.")) # noqa
        return True
