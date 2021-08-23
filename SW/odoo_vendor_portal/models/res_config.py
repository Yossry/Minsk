# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    done_rfq_basedon = fields.Selection([
        ('price', 'Minimum quoted price'),
        ('delivery', 'Minimum delivery time'),
        ], "Vendor RFQ",
        help='On closing date of vendor RFQs, vendor will be select accordingly in order to done the RFQs by scheduler')
    msg_quote_submit = fields.Text(string="Message Qoute Submisison",
        help="Message will be visible on the RFQ page to the vendor after submit their quote")
    msg_quote_accecpt = fields.Text(string="Message Qoute Accept",
        help="Message will be visible on the RFQ page to the vendor after accecpting their quote by admin/manager")
    msg_quote_reject = fields.Text(string="Message Qoute Reject",
        help="Message will be visible on the RFQ page to the vendor if the vendor quote is not get accepted")
    msg_rfq_cancel = fields.Text(string="Message RFQ Cancel",
        help="Message will be visible on the RFQ page to the vendor for the cancelled RFQ ")
    msg_po_create = fields.Text(string="Message Purchase Order",
        help="Message will be visible on the RFQ page to the vendor after PO created for their RFQ")

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.done_rfq_basedon", self.done_rfq_basedon
        )
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.msg_quote_submit", self.msg_quote_submit
        )
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.msg_quote_accecpt", self.msg_quote_accecpt
        )
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.msg_quote_reject", self.msg_quote_reject
        )
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.msg_rfq_cancel", self.msg_rfq_cancel
        )
        IrConfigPrmtr.set_param(
            "odoo_vendor_portal.msg_po_create", self.msg_po_create
        )


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        res.update({
            'done_rfq_basedon' : IrConfigPrmtr.get_param('odoo_vendor_portal.done_rfq_basedon'),
            'msg_quote_submit' : IrConfigPrmtr.get_param('odoo_vendor_portal.msg_quote_submit'),
            'msg_quote_accecpt' : IrConfigPrmtr.get_param('odoo_vendor_portal.msg_quote_accecpt'),
            'msg_quote_reject' : IrConfigPrmtr.get_param('odoo_vendor_portal.msg_quote_reject'),
            'msg_rfq_cancel' : IrConfigPrmtr.get_param('odoo_vendor_portal.msg_rfq_cancel'),
            'msg_po_create' : IrConfigPrmtr.get_param('odoo_vendor_portal.msg_po_create'),
        })
        return res