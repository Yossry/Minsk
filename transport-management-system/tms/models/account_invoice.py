# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    waybill_ids = fields.One2many(
        'tms.waybill', 'invoice_id', string="Waybills", readonly=True)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if not self.waybill_ids:
            return super(AccountInvoice, self)._onchange_journal_id()
        self.currency_id = self.waybill_ids[0].currency_id.id
        return True
