# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    note = fields.Text()

