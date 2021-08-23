# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _refund_cleanup_lines(self, lines):
        for line in lines:
            if not line.origin_invoice_line_id:
                line.origin_invoice_line_id = line.id
        res = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        for line in lines:
            if line == line.origin_invoice_line_id:
                line.origin_invoice_line_id = False
        return res
