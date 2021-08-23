# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import operator
from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError


class VendorRfq(models.Model):
    _name = 'vendor.rfq'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vendor RFQ"
    _order = 'create_date desc, id desc'

    @api.model
    def _update_settings(self):
        configModel = self.env['res.config.settings']
        defaultSetObj = configModel.create({'done_rfq_basedon' : 'price'})
        defaultSetObj.execute()
        return True

    @api.depends('product_id', 'pricelist_id',)
    def _product_sale_price(self):
        for rfqObj in self:
            if rfqObj.pricelist_id and rfqObj.product_id:
                salePrice = rfqObj.product_id.with_context(pricelist=rfqObj.pricelist_id.id).price
                costPrice = rfqObj.product_id.standard_price
                currencyObj = rfqObj.pricelist_id.currency_id
                productUom = rfqObj.product_uom or False
                if not productUom:
                    productUom = self.product_id.uom_po_id or self.product_id.uom_id
                currencyId = currencyObj.id
                prodCrncy = self.product_id.currency_id
                costPrice = prodCrncy.compute(costPrice, currencyObj)
                rfqObj.update({
                    'currency_id' : currencyId,
                    'product_sale_price' : salePrice,
                    'product_cost' : costPrice,
                    'product_uom' : productUom and productUom.id or False
                })


    name = fields.Char(string='RFQ Reference', required=True, copy=False,
        readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sent', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    user_id = fields.Many2one(
        'res.users', string='RFQ Manager', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, help="Pricelist for calculating RFQ and PO currency")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", store=True, readonly=True, compute='_product_sale_price', help="Currency for PO")
    product_id = fields.Many2one(
        'product.product', string="Product", required=True, readonly=True, states={'draft': [('readonly', False)], 'pending': [('readonly', False)]})
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    product_image = fields.Binary('Product Image', related="product_id.image", store=False)
    product_cost = fields.Monetary(string="Cost Price", readonly=True, store=True, compute='_product_sale_price', help="Product cost price")
    product_sale_price = fields.Monetary(string="Sale Price", store=True, readonly=True, compute='_product_sale_price', help="Product sale price")
    prod_qty = fields.Float(
        string="Quantity", required=True, default=1.0, readonly=True, states={'draft': [('readonly', False)], 'pending': [('readonly', False)]})
    est_unit_price = fields.Monetary(
        string="Our Estimated Quote", readonly=True,
        states={'draft': [('readonly', False)], 'pending': [('readonly', False)]},
        help="Admin/Managers can set their estimated quote per unit for this rfq, this information will be sent to the vendors.")
    create_date = fields.Datetime(
        string="Created Date", required=True, readonly=True, copy=False, default=fields.Datetime.now)
    est_del_date = fields.Date(
        string="Our Estimated Delivery", copy=False, readonly=True,
        states={'draft': [('readonly', False)], 'pending': [('readonly', False)]},
        help="Admin/Managers can set their estimated delivery date for this rfq, this information will be sent to the vendors.")
    close_date = fields.Date(
        string="RFQ Closing Date", copy=False, readonly=True,
        states={'draft': [('readonly', False)], 'pending': [('readonly', False)]}, help="Last date of quatation for the vendor")
    vendor_ids = fields.Many2many(
        'res.partner', 'wk_vendor_rfq_rel', 'wkrfq_id', 'wkvedor_id', string="Vendors", required=True,
        domain=[('supplier', '=', True)], copy=False, readonly=True, states={'draft': [('readonly', False)]},
        help="Admin/Managers can add the vendors and invite for this RFQ")
    vendor_rfq_history = fields.One2many(
        'vendor.rfqhistory', 'vendorrfq_id', string="Suppliers", copy=False,
        help="Quoted history by the vendors for the RFQ")
    assign_vendor = fields.Many2one(
        'res.partner', string='Assigned Vendor', copy=False, readonly=True, help="Selected vendor for creating PO")
    assign_vendor_price = fields.Float()
    order_create = fields.Boolean()
    vendor_del_date = fields.Date(string="Vendor Delivery Date")
    po_order = fields.Many2one('purchase.order', string="PO")
    notes = fields.Text(string="Note", help="Addition note for the vendors")

    @api.onchange('product_id')
    def onchange_add_vendors(self):
        self.ensure_one()
        prodObj = self.product_id
        if prodObj:
            prodSeller = prodObj.seller_ids
            prodVendorIds = prodSeller.mapped('name').ids
            if prodVendorIds:
                self.vendor_ids = [(6, 0, prodVendorIds)]
            else:
                self.vendor_ids = [(6, 0, [])]


    @api.constrains('est_del_date', 'close_date')
    def check_date(self):
        self.ensure_one()
        if self.close_date and self.est_del_date and self.close_date >= self.est_del_date:
            raise ValidationError("Estimated Delivery Date must be greater than Closing date!")
        elif self.close_date and self.create_date.date() >= self.close_date:
            raise ValidationError("Closing Date must be greater than Create date!")
        if self.est_del_date and self.create_date.date() >= self.est_del_date:
            raise ValidationError("Estimated Delivery Date must be greater than Created date!")

    @api.multi
    def action_draft(self):
        self.ensure_one()
        if self.state == 'cancel':
            self.state = 'draft'
        return True

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancel'
        return True

    @api.multi
    def action_pending(self):
        self.ensure_one()
        self.state = 'pending'
        return True

    @api.multi
    def create_po(self):
        self.ensure_one()
        puchaseModel = self.env['purchase.order']
        pOrderLineModel = self.env['purchase.order.line']
        purchaseOrder = puchaseModel.create({
            'partner_id' : self.assign_vendor.id,
            'currency_id' : self.currency_id.id,
            'vendor_del_date' : self.vendor_del_date
            })
        purchaseOrder.onchange_partner_id()
        purchaseOrder.currency_id = self.currency_id.id
        pOrderLine = pOrderLineModel.create({
            'product_id' : self.product_id.id,
            'name' : self.product_id.name,
            'order_id' : purchaseOrder.id,
            'price_unit' : self.assign_vendor_price,
            'product_qty' : self.prod_qty,
            'product_uom' : self.product_uom.id,
            'date_planned' : datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        })
        pOrderLine.onchange_product_id()
        pOrderLine.price_unit = self.assign_vendor_price
        pOrderLine.product_qty = self.prod_qty
        pOrderLine.product_uom = self.product_uom.id
        self.order_create = True
        self.po_order = purchaseOrder.id
        return True

    @api.multi
    def purchase_order_view(self):
        self.ensure_one()
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        poId = self.po_order.id
        if poId:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = poId
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.rfq') or 'New'
        return super(VendorRfq, self).create(vals)

    @api.multi
    def action_rfq_mail_send(self):
        self.ensure_one()
        delDate = self.est_del_date
        if delDate:
            month = delDate.strftime("%B")
            day = delDate.day
            year = delDate.year
            delDate = "{} {}, {}".format(month, day, year)
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        templXmlId = irModelData.get_object_reference('odoo_vendor_portal', 'email_template_edi_selller_rfq')[1]
        vendorObjs = self.vendor_ids
        baseUrl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirectUrl = baseUrl + "/my/rfqrequests/" + str(self.id)
        if templXmlId and vendorObjs:
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            for vendor in vendorObjs:
                ctx = {
                    'wkemail' : vendor.email,
                    'wkname' : vendor.name,
                    'wkDate' : delDate,
                    'lang' : vendor.lang,
                    'redirectUrl' : redirectUrl
                }
                mailTmplObj.with_context(**ctx).send_mail(self.id, force_send=True)
            self.state = 'sent'
        else:
            raise ValidationError(
            _('First add the Vendors'))

    @api.model
    def send_mail_done(self, rfqObj, vebdorPrice=None, vendorDate=None, vendorObj=None):
        mailTemplateModel = self.env['mail.template']
        irModelData = self.env['ir.model.data']
        templXmlId = irModelData.get_object_reference('odoo_vendor_portal', 'email_template_edi_rfq_done')[1]
        date_format = '%Y-%m-%d'
        delDate = datetime.strptime(vendorDate, date_format)
        month = delDate.strftime("%b")
        day = delDate.strftime("%d")
        year = delDate.strftime("%Y")
        delDate = "{} {}, {}".format(month, day, year)
        if templXmlId and rfqObj:
            mailTmplObj = mailTemplateModel.browse(templXmlId)
            ctx = {
                'wkemail' : vendorObj.email,
                'wkname' : vendorObj.name,
                'lang' : vendorObj.lang,
                'wkprice' : vebdorPrice,
                'wkDate' : delDate,
                'lang' : vendorObj.lang,
            }
            mailTmplObj.with_context(**ctx).send_mail(rfqObj.id, force_send=True)

    @api.multi
    def action_view_rfq(self):
        self.ensure_one()
        baseUrl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirectUrl = baseUrl + "/my/rfqrequests/" + str(self.id)
        return {
            'type': 'ir.actions.act_url',
            'url': redirectUrl,
            'target': 'self',
            'res_id': self.id,
        }

    @api.multi
    def action_view_po(self):
        self.ensure_one()
        baseUrl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        redirectUrl = baseUrl + "/my/purchase/" + str(self.po_order.id)
        return {
            'type': 'ir.actions.act_url',
            'url': redirectUrl,
            'target': 'self',
            'res_id': self.po_order.id,
        }

    @api.multi
    def wk_vendor_done(self):
        wizObj = self.env['vendor.rfq.done'].create({})
        ctx = dict(self._context or {})
        return {'name': "Mark Done RFQ",
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'vendor.rfq.done',
                'res_id': wizObj.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                }

    @api.model
    def update_vendor_history(self, rfqId, offerPrice, offerDate, offerNote, splrUserId):
        vendorPartnerObj = self.env['res.users'].sudo().browse(splrUserId).partner_id
        rfqObj = self.env['vendor.rfq'].sudo().browse(rfqId)
        rfqHistoryModel = self.env['vendor.rfqhistory'].sudo()
        vals = {
            'name' : vendorPartnerObj.id,
            'currency_id' : rfqObj.currency_id.id,
            'quoted_price' : offerPrice,
            'quoted_del_date' : offerDate or '',
            'quoted_note' : offerNote or '',
            'vendorrfq_id' : rfqId,
        }
        res = rfqHistoryModel.create(vals)
        return rfqId