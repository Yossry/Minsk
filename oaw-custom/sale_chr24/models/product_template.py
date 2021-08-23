# Copyright 2020 Quartile Limited, Timeware Limited

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    chrono = fields.Boolean(string="Active In Chrono24", default=False)
    chrono24_updated = fields.Boolean(string="Updated-Please Check", default=False)
    chronoNote = fields.Char(string="Note Chrono24")
    updated_date_chrono24 = fields.Datetime(
        store=True, default=False, string="Updated Chrono24 Date"
    )
    chrono24_price = fields.Float(string="Chrono24 Price", store=True)

    @api.multi
    def updated_chrono24_date(self, pt, vals):
        if "qty_local_stock" in vals and "qty_reserved" in vals:
            if vals["qty_local_stock"] - vals["qty_reserved"] >= 0:
                return True
        elif "qty_local_stock" in vals:
            if vals["qty_local_stock"] - pt.qty_reserved >= 0:
                return True
        elif "qty_reserved" in vals:
            if pt.qty_local_stock - vals["qty_reserved"] >= 0:
                return True
        elif "list_price" in vals:
            if pt.list_price != vals["list_price"]:
                return True
        elif "stock_cost" in vals:
            if pt.stock_cost != vals["stock_cost"]:
                return True
        elif "net_price" in vals:
            if pt.net_price != vals["net_price"]:
                return True
        elif "chrono24_price" in vals:
            if pt.chrono24_price != vals["chrono24_price"]:
                return True
        return False

    @api.multi
    def write(self, vals):
        for pt in self:
            if pt.chrono:
                if (
                    "list_price" in vals
                    or "net_price" in vals
                    or "stock_cost" in vals
                    or "chrono24_price" in vals
                    or "qty_reserved" in vals
                    or "qty_local_stock" in vals
                    or "qty_overseas" in vals
                ):
                    if self.updated_chrono24_date(pt, vals):
                        pt.updated_date_chrono24 = fields.Datetime.now()
                        pt.chrono24_updated = True
            if "chrono" in vals:
                if vals["chrono"]:
                    pt.updated_date_chrono24 = fields.Datetime.now()
                    pt.chrono24_updated = True
        return super(ProductTemplate, self).write(vals)
