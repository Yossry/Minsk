# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_data_product_id = fields.Many2one(
        "product.product", "Supplier Purchase Stock Data Product"
    )
    local_loc_id = fields.Many2one(
        "supplier.location", "Local Supplier Location for Stock Data"
    )
    oversea_loc_id = fields.Many2one(
        "supplier.location", "Oversea Supplier Location for Stock Data"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        res.update(
            purchase_data_product_id=int(
                get_param(
                    "supplier_user_stock_data_purchase.purchase_data_product_id",
                    default=False,
                )
            )
        )
        res.update(
            local_loc_id=int(
                get_param(
                    "supplier_user_stock_data_purchase.local_loc_id", default=False,
                )
            )
        )
        res.update(
            oversea_loc_id=int(
                get_param(
                    "supplier_user_stock_data_purchase.oversea_loc_id", default=False,
                )
            )
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env["ir.config_parameter"].sudo().set_param
        set_param(
            "supplier_user_stock_data_purchase.purchase_data_product_id",
            self.purchase_data_product_id.id,
        )
        set_param(
            "supplier_user_stock_data_purchase.local_loc_id", self.local_loc_id.id,
        )
        set_param(
            "supplier_user_stock_data_purchase.oversea_loc_id", self.oversea_loc_id.id,
        )
