# Copyright 2019 chrono123 & Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    currency_price_change_date = fields.Datetime(
        string="Last Update on Currency Amount"
    )
    # For a filter in Supplier Stock
    # Trigger:  supplier_stock.create()
    new_entry_date = fields.Datetime(string="New Supplier Stock")

    # Resetting Offer Checked Button
    def update_product_template(self, vals):
        pt = self.product_id.product_tmpl_id
        if "quantity" in vals:
            pt.sudo().write({"partner_offer_checked": False})
            current_quantity = self.quantity
            if current_quantity < vals["quantity"]:
                pt.sudo().write({"qty_up": True})
            elif current_quantity > vals["quantity"]:
                pt.sudo().write({"qty_down": True})
        if "price_unit" in vals:
            pt.sudo().write(
                {
                    "currency_price_change_date": fields.Datetime.now(),
                    "partner_offer_checked": False,
                }
            )
            current_price_unit = self.price_unit
            if current_price_unit < vals["price_unit"]:
                pt.sudo().write({"costprice_up": True})
            elif current_price_unit > vals["price_unit"]:
                pt.sudo().write({"costprice_down": True})
        if "partner_note" in vals:
            pt.sudo().write({"note_updated": True, "partner_offer_checked": False})

    @api.multi
    def write(self, vals):
        for ps in self:
            ps.update_product_template(vals)
            # Purchase Price/Currency Price change -> Supplier Stocks
            # 'currency_price_change_date' gets updated
            if "price_unit" in vals:
                vals["currency_price_change_date"] = fields.Datetime.now()
        return super(SupplierStock, self).write(vals)

    # 1.) set date in product template if the template used for partner stock
    #     creation hasnt been used before
    # 2.) duplicate entry with different purchase price impacting PLU filter
    # 3.) duplicate entry with same price, might be from different supplier
    @api.model
    def create(self, vals):
        if "product_id" in vals and "currency_id" in vals:
            # New Entry for product and supplier_stock
            vals["new_entry_date"] = fields.Datetime.now()
            domain_templates = [("id", "=", vals["product_id"])]
            templates = self.env["product.product"].search(
                domain_templates, order="create_date DESC"
            )
            if templates:
                templates[0].product_tmpl_id.sudo().write(
                    {"new_entry_date": fields.Datetime.now()}
                )
            # Currency Price changed
            domain_similar_entries = [
                ("product_id", "=", vals["product_id"]),
                ("currency_id", "=", vals["currency_id"]),
            ]
            last_added_entries = self.search(
                domain_similar_entries, order="create_date DESC"
            )
            if last_added_entries:
                if last_added_entries[0].price_unit != vals["price_unit"]:
                    vals["currency_price_change_date"] = fields.Datetime.now()
                    last_added_entries[0].product_id.product_tmpl_id.sudo().write(
                        {"currency_price_change_date": fields.Datetime.now()}
                    )
        return super(SupplierStock, self).create(vals)
