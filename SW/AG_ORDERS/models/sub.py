# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools ,_
from odoo.exceptions import except_orm, ValidationError,UserError
from odoo.exceptions import  AccessError, UserError, RedirectWarning,Warning
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta , date
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.exceptions
import re 
from odoo.http import request
from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
from ast import literal_eval
from odoo.addons.web.controllers.main import clean_action

class OrdersForm(models.Model):
    _name = "orders.form"
    # _inherit = ''

    restaurant_name  = fields.Many2one('res.partner',string="Restaurant name ")
    order_time  = fields.Datetime('Order Time ')
    name  = fields.Char('Order ID')
    customer_name  = fields.Char('Customer Name')
    delivery_mode  = fields.Selection([
            ('Home Delivery', 'Home Delivery'),
            ('Take Away', 'Take Away')], string='Delivery Mode',
            default='Home Delivery', copy=False)
    order_value  = fields.Float('Order Value')
    discount  = fields.Float('Discount')
    promo_discount  = fields.Float('Promo Discount')
    promo_code = fields.Char('Promo Code')
    loyalty_points  = fields.Float('Redeemed Loyalty Points')
    paid_amount  = fields.Float('Paid Amt')
    payment_method  = fields.Char('Payment Method')
    gateway_charges  = fields.Float('Gateway Charges')
    commission_amount  = fields.Float('Commission Amount')
    settilment_amount  = fields.Float('Settilment Amount')



   
    