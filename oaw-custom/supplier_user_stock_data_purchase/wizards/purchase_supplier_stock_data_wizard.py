# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseSupplierStockDataWizard(models.TransientModel):
    _name = "purchase.supplier.stock.data.wizard"

    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        default=lambda self: self.env.user.partner_id.commercial_partner_id,
    )
    product_category_ids = fields.Many2many(
        "product.category", string="Brands", required=True,
    )
    purchased_category_ids = fields.Many2many(
        "product.category",
        string="Purchased Band",
        compute="_compute_purchased_category_ids",
    )
    total_price = fields.Float(string="Total Price (HKD)",)

    def action_purchase_data(self):
        purchase_categories = self.product_category_ids
        purchase_data_product_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("supplier_user_stock_data_purchase.purchase_data_product_id")
        )
        website_team_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("website_sale.salesteam_id")
        )
        total_price = sum(purchase_categories.mapped("stock_data_purchase_price"))
        order_vals = {
            "partner_id": self.supplier_id.id,
            "company_id": self.env.user.company_id.id,
            "require_payment": True,
            "state": "draft",
        }
        sale_order = self.env["sale.order"].sudo().create(order_vals)
        sale_order.onchange_partner_id()
        sale_order.pricelist_id = (
            self.env["product.pricelist"]
            .search(
                [("currency_id", "=", self.env.user.company_id.currency_id.id)], limit=1
            )
            .id
        )
        sale_order.team_id = website_team_id
        line_vals = {
            "product_id": int(purchase_data_product_id),
            "company_id": self.env.user.company_id.id,
            "product_uom_qty": 1.0,
            "price_unit": total_price,
            "order_id": sale_order.id,
            "name": "\n".join(purchase_categories.mapped("name")),
        }
        self.env["sale.order.line"].sudo().create(line_vals)
        sale_order.state = "sent"
        self.env["stock.data.purchase.history"].sudo().create(
            {
                "supplier_id": self.supplier_id.id,
                "product_category_ids": [(6, 0, self.product_category_ids.ids)],
                "sale_order_id": sale_order.id,
                "purchase_date": fields.Datetime.now(),
                "payment_confirm": False,
            }
        )
        return sale_order.preview_sale_order()

    @api.onchange("product_category_ids", "supplier_id")
    def _onchange_total_price(self):
        if self.product_category_ids:
            self.total_price = sum(
                self.product_category_ids.mapped("stock_data_purchase_price")
            )
        if self.supplier_id:
            self._compute_purchased_category_ids()
        all_product_categories = self.supplier_id.product_category_ids or self.env[
            "product.category"
        ].search([("supplier_access", "=", True)])
        product_category_ids = list(
            set(all_product_categories.ids) - set(self.purchased_category_ids.ids)
        )
        return {
            "domain": {"product_category_ids": [("id", "in", product_category_ids)]}
        }

    @api.multi
    def _compute_purchased_category_ids(self):
        for wizard in self:
            purchase_history = self.env["stock.data.purchase.history"].search(
                [
                    ("supplier_id", "=", wizard.supplier_id.id),
                    ("payment_confirm", "=", True),
                ]
            )
            wizard.purchased_category_ids = purchase_history.mapped(
                "product_category_ids"
            )
