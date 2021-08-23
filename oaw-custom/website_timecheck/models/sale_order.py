# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_method = fields.Selection(
        selection=[
            ("china_bank_transfer", "China Bank Transfer"),
            ("hk_bank_cheque", "Hong Kong Banks' Cheque"),
            ("direct_bank_transfer", "Bank Transfer to our HK company"),
            ("visa_union_pay", "Visa or Union (Extra 2.2% as fee)"),
            ("other", "Other Payment Method"),
        ],
        string="Payment Method",
    )
    payment_desc = fields.Char(string="Other Payment Method")
    picking_date = fields.Date(
        string="Desire Picking Date", help="Monday to Friday 15:00-18:00"
    )
    other_inquiry = fields.Char(string="Other Inquiry")

    # According to the user group and price settings, update the price with
    # portal user adds product to cart.
    def _cart_update(
        self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs
    ):
        res = super(SaleOrder, self)._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs
        )
        if "line_id" in res and res["line_id"]:
            order_line = self.env["sale.order.line"].browse(res["line_id"])
            product = order_line.product_id
            if product.sale_hkd_ac_so:
                order_line.price_unit = product.sale_hkd_ac_so
            else:
                partner_id = order_line.order_id.partner_id
                if partner_id.user_ids and partner_id.user_ids[0].has_group(
                    "website_timecheck.group_timecheck_light"
                ):
                    order_line.price_unit = product.sale_hkd_ac
                elif (
                    product.qty_overseas != 0
                    and product.oversea_retail_currency_id
                    == product.company_id.currency_id
                    and product.price > product.oversea_retail_price
                ):
                    order_line.price_unit = product.oversea_retail_price
                else:
                    order_line.price_unit = product.list_price
        return res
