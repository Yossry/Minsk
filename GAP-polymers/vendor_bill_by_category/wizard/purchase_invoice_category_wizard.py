# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)


class PurchaseInvoiceCategroyWizard(models.TransientModel):
    _name = 'purchase.invoice.category.wizard'
    _description = 'Vendor Bill by Product Category'

    category_ids = fields.Many2many(comodel_name="product.category")
    restricted_category_ids = fields.Many2many(comodel_name="product.category",default=lambda r:r.default_categories(),compute='compute_restricted_category_ids')

    def get_categorie_from_purchase(self):
        purchase_order_id = self.env.context.get('active_id')
        if purchase_order_id:
            purchase_order = self.env['purchase.order'].browse(purchase_order_id)
            lines = purchase_order.order_line
            category_ids = lines.mapped('product_id.categ_id')
            return category_ids
        else:
            return None

    def default_categories(self):
            categories = self.get_categorie_from_purchase()
            return categories.ids

    @api.constrains('category_ids')
    def check_categories(self):
        if not self.category_ids:
            raise ValidationError(_('You Did not Select Any Product Category'))

    def compute_restricted_category_ids(self):
        self.restricted_category_ids = self.get_categorie_from_purchase()

    def action_create_invoices(self):
        product_categories = self.category_ids
        categ_invoice_lines = {}
        purchase_order_id = self.env.context.get('active_id')
        if purchase_order_id:
            purchase_order = self.env['purchase.order'].browse(purchase_order_id)
            invoice_values = {
                'type': 'in_invoice',
                'origin': purchase_order.name,
                'purchase_id': purchase_order.id,
                'currency_id': purchase_order.currency_id.id,
                'company_id': purchase_order.company_id.id,
                'partner_id': purchase_order.partner_id.id,
                'payment_term_id': purchase_order.payment_term_id.id,
            }
            for line in purchase_order.order_line.filtered(lambda l:l.product_id.categ_id.id in product_categories.ids):
                categ = line.product_id.categ_id
                if categ not in categ_invoice_lines:
                    categ_invoice_lines[categ] = []

                categ_invoice_lines[categ].append(line)

            for categ in categ_invoice_lines.keys():
                bill = self.env['account.invoice'].create(invoice_values.copy())
                bill._onchange_partner_id()
                purchase_lines = categ_invoice_lines[categ]

                new_lines = self.env['account.invoice.line']
                for line in purchase_lines:
                    invoice_line_vals = bill._prepare_invoice_line_from_po_line(line)
                    invoice_line_vals['invoice_id'] = bill.id
                    invoice_line_vals['quantity'] = line.product_qty
                    new_line = new_lines.create(invoice_line_vals)
                    new_line._set_additional_fields(bill)

            return purchase_order.action_view_invoice()





