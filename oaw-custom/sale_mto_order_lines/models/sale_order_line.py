# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    prod_ref = fields.Char(
        related="product_id.product_tmpl_id.name",
        string="Product Reference",
        store=True,
    )
    prod_code = fields.Char(
        related="product_id.product_tmpl_id.default_code", string="Code", store=True
    )
    is_mto = fields.Boolean(string="MTO", related="order_id.is_mto")
    order_price_list = fields.Char(
        related="order_id.pricelist_id.name", string="Price List"
    )
    order_date = fields.Datetime(related="order_id.date_order", string="Date")
    supplier_code = fields.Char(
        "Supplier Code", related="order_id.supplier_code", store=True
    )
    supplier_note = fields.Char("Supplier Notes")
    sales_remark = fields.Char("Sales Team Remark")
