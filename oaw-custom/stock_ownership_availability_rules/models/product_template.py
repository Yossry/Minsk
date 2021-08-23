# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_open_quants(self):
        result = super(ProductTemplate, self).action_open_quants()
        result["context"] = {
            "search_default_locationgroup": 1,
            "search_default_ownergroup": 1,
            "search_default_internal_loc": 1,
        }
        return result
