# Copyright 2019 chrono123 & Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    category_name = fields.Char(string="Brand", related="categ_id.name")
    additional_info = fields.Char(string="Additional Info")
    # For a filter in Product and Product Offer views.
    # Trigger: VCI Receipt (stock.quant (stock_move.purchase_price_unit)),
    # Supplier Stock Creation/Modification (supplier_stock.price_unit)
    currency_price_change_date = fields.Datetime(
        string="Currency Amount Price Change Date"
    )
    # For Filter Retail Changed 24H
    # Effective in Product and Product Offer
    # Trigger: product_template.list_price "Retail HKD"
    list_price_change_date = fields.Datetime(
        string="Retail HKD Change Date",
        store=True,
        compute="_compute_list_price_change_date",
    )
    # Trigger: stock_quant.create(), supplier_stock.create()
    new_entry_date = fields.Datetime(string="New Entry")
    # Resetting Offer Checked Button
    partner_offer_checked = fields.Boolean(string="Offer Checked", default=False)
    qty_up = fields.Boolean(string="Partner Quantity increased")
    qty_down = fields.Boolean(string="Partner Quantity decreased")
    costprice_up = fields.Boolean(string="Partner Sale Price inc.", readonly=True)
    costprice_down = fields.Boolean(string="Partner Sale Price dec.", readonly=True)
    note_updated = fields.Boolean(string="Partner Note updated")
    # For a filter in Product and Product Offer
    # Trigger: product_template.write(),
    # Trigger: product_product.price_up_date
    price_up_date = fields.Datetime(string="Sale HKD Price Up Date")
    # For a filter in Product and Product Offer
    # Trigger: product_template.write(),
    # Trigger: product_product.price_up_date
    price_down_date = fields.Datetime(string="Sale HKD Price Down Date")

    @api.multi
    @api.depends("list_price")
    def _compute_list_price_change_date(self):
        for pt in self:
            pt.list_price_change_date = fields.Datetime.now()

    @api.multi
    def write(self, vals):
        for pt in self:
            # For a filter based on the date when AA price has been changed.
            if "net_price" in vals:
                curr_net_price = pt.net_price
                if curr_net_price < vals["net_price"]:
                    vals["price_up_date"] = fields.Datetime.now()
                elif curr_net_price > vals["net_price"]:
                    vals["price_down_date"] = fields.Datetime.now()
            # Resetting Offer Checked Button
            if "qty_local_stock" in vals and "qty_reserved" in vals:
                if vals["qty_local_stock"] - vals["qty_reserved"] == 0:
                    vals["partner_offer_checked"] = False
                    self.partner_offer_checked = False
            elif "qty_local_stock" in vals:
                if vals["qty_local_stock"] - pt.qty_reserved == 0:
                    vals["partner_offer_checked"] = False
        return super(ProductTemplate, self).write(vals)
