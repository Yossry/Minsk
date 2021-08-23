# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_new_arrival = fields.Datetime(string="New Arrival")
    special_offer_limit = fields.Datetime(string="Special Offer Limit")
    in_special_offer_limit = fields.Boolean(
        string="Special Offer Limit", compute="_compute_in_special_offer_limit"
    )
    is_new_arrival = fields.Boolean(
        string="New Arrival", compute="_compute_is_new_arrival"
    )
    website_product_seq_date = fields.Datetime(
        string="Product Sequence Date",
        compute="_compute_website_product_seq_date",
        store=True,
    )

    @api.multi
    def _compute_in_special_offer_limit(self):
        for product in self:
            if self.env.user.has_group("website_timecheck.group_timecheck_light"):
                product.in_special_offer_limit = False
            else:
                product.in_special_offer_limit = (
                    True
                    if product.special_offer_limit
                    and product.special_offer_limit >= datetime.datetime.now()
                    or not product.special_offer_limit
                    else False
                )

    @api.multi
    def _compute_is_new_arrival(self):
        for product in self:
            now = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
            product.is_new_arrival = (
                True
                if product.stock_new_arrival and product.stock_new_arrival >= now
                else False
            )

    @api.multi
    def write(self, vals):
        if (
            "qty_local_stock" in vals
            or "qty_overseas" in vals
            or "qty_reserved" in vals
        ):
            for product in self:
                qty_local_stock = vals.get("qty_local_stock", product.qty_local_stock)
                qty_overseas = vals.get("qty_overseas", product.qty_overseas)
                qty_reserved = vals.get("qty_reserved", product.qty_reserved)
                if (
                    product.qty_overseas < qty_overseas
                    or product.qty_local_stock < qty_local_stock
                    and qty_local_stock > qty_reserved
                ):
                    product.sudo().write({"stock_new_arrival": fields.Datetime.now()})
                elif qty_local_stock == qty_reserved:
                    product.sudo().write({"stock_new_arrival": False})
        if "sale_hkd_ac_so" in vals and vals["sale_hkd_ac_so"]:
            special_offer_limit = datetime.datetime.now() + datetime.timedelta(days=+3)
            vals["special_offer_limit"] = special_offer_limit
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def update_public_category(self):
        for product in self:
            if product.categ_id and not product.public_categ_ids:
                public_categ_ids = self.env["product.public.category"].search(
                    [("name", "=", product.categ_id.name)]
                )
                product.public_categ_ids = public_categ_ids

    @api.multi
    def reset_public_category(self):
        for product in self:
            product.public_categ_ids = False

    @api.multi
    @api.depends("partner_stock_last_modified", "last_in_date")
    def _compute_website_product_seq_date(self):
        for product in self:
            product.website_product_seq_date = (
                product.last_in_date or product.partner_stock_last_modified
            )
            if (
                product.last_in_date
                and product.partner_stock_last_modified
                and product.partner_stock_last_modified > product.last_in_date
            ):
                product.website_product_seq_date = product.partner_stock_last_modified

    @api.multi
    def _update_website_product_seq_date(self):
        for product in self:
            product.website_product_seq_date = fields.Datetime.now()
