# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    partner_type = fields.Selection(selection_add=[("seller", "Seller")])

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        for pay in self.filtered(lambda p: p.invoice_ids):
            payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
            pay.payment_difference = pay._compute_payment_amount() - payment_amount
            if self._context.get("active_model", False) == "seller.payment":
                pay.payment_difference = abs(self.env["seller.payment"].browse(
                    pay._context["active_id"]).payable_amount) - pay.amount

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        ctx = self._context.copy()
        active_id = ctx.get('active_id')
        active_model = ctx.get('active_model')
        if not active_id or active_model != 'account.invoice':
            return rec
        invoice = self.env['account.invoice'].browse(active_id)
        if invoice and invoice.is_seller and invoice.seller_payment_ids:
            rec["partner_type"] = "seller"
            rec["payment_type"] = "outbound"
        return rec

    @api.multi
    def post(self):
        for rec in self:
            sequence_code = False
            if not rec.name and rec.payment_type != 'transfer' and rec.partner_type == 'seller':
                if rec.payment_type == 'inbound':
                    sequence_code = rec.env.ref('odoo_marketplace.sequence_payment_seller_refund')
                if rec.payment_type == 'outbound':
                    sequence_code = rec.env.ref('odoo_marketplace.sequence_payment_seller_invoice')
            if sequence_code:
                rec.name = sequence_code.with_context(ir_sequence_date=rec.payment_date).next_by_id()
        return super(AccountPayment, self).post()
