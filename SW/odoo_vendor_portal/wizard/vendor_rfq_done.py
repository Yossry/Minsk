# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from lxml import etree

from odoo import api, fields, models, _


class VendorRfqDone(models.TransientModel):
    _name = 'vendor.rfq.done'

    assign_vendor_id = fields.Many2one('res.partner', string="Selected Vendor", help="Vendor will be select for this RFQ in order to create PO")
    currency_id = fields.Many2one("res.currency", string="Currency")
    quoted_price = fields.Monetary(string="Quoted Price", readonly=True, help="Quoted price by the vendor")
    quoted_del_date = fields.Date(string="Quoted Delivery Date", readonly=True, help="Quoted delivery date by the vendor")


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(VendorRfqDone, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
        rfqId = self._context.get('active_id')
        rfqObj = self.env['vendor.rfq'].browse(rfqId)
        historyObjs = rfqObj.vendor_rfq_history
        inrstdVendorIds = historyObjs.mapped('name').ids
        doc = etree.XML(res['arch'])
        node = doc.xpath("//field[@name='assign_vendor_id']")[0]
        node.set('domain', "[('id', 'in' , ["+','.join(map(str, inrstdVendorIds)) +"] )]")
        res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('assign_vendor_id')
    def update_wizard_view(self):
        self.ensure_one()
        if self.assign_vendor_id:
            rfqId = self._context.get('active_id')
            rfqHistory = self.env['vendor.rfqhistory'].search([
                ('name', '=', self.assign_vendor_id.id),
                ('vendorrfq_id', '=', rfqId)])
            if rfqHistory:
                self.currency_id = rfqHistory.currency_id.id
                self.quoted_price = rfqHistory.quoted_price
                self.quoted_del_date = rfqHistory.quoted_del_date

    @api.multi
    def mark_done(self):
        self.ensure_one()
        rfqId = self._context.get('active_id')
        vendorId = self.assign_vendor_id.id
        vendorModel = self.env['vendor.rfq']
        rfqObj = vendorModel.browse(rfqId)
        quotedDetails = self.env['vendor.rfqhistory'].search([('name', '=', vendorId),('vendorrfq_id', '=', rfqId)])
        if quotedDetails:
            try :
                rfqObj.assign_vendor = vendorId
                rfqObj.assign_vendor_price = quotedDetails.quoted_price
                if quotedDetails.quoted_del_date:
                    rfqObj.vendor_del_date = quotedDetails.quoted_del_date
                rfqObj.state = 'done'
                vendorModel.send_mail_done(rfqObj, quotedDetails.quoted_price, quotedDetails.quoted_del_date, self.assign_vendor_id)
            except Exception as e:
                pass
        return True