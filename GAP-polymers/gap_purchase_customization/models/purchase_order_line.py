# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    note = fields.Text()

