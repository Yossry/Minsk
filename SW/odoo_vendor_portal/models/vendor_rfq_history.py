# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class BidSupplierInfo(models.Model):
    _name = 'vendor.rfqhistory'
    _description = "Vendor RFQ history"

    name = fields.Many2one(
        'res.partner', 'Vendor',
        domain=[('supplier', '=', True)], ondelete='cascade', required=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    quoted_price = fields.Monetary(string="Quoted Price", required=True)
    quoted_del_date = fields.Date(string="Delivery Date", required=True)
    quoted_note = fields.Text(string="Vendor Note")
    vendorrfq_id = fields.Many2one(
        'vendor.rfq', 'Product Vendor RFQ',
        required=True, index=True, ondelete='cascade')


    @api.onchange('vendorrfq_id')
    def set_currency(self):
        if self.vendorrfq_id:
            self.currency_id = self.vendorrfq_id.currency_id.id
