# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_id = fields.Many2one(
        default=lambda self: self._default_picking_type_id()
    )

    def _default_picking_type_id(self):
        context = self.env.context or {}
        # following two lines may not be needed - default from window action
        # probably overrides the _defaults setting of picking_type_id
        if context.get("default_picking_type_id", False):
            return context["default_picking_type_id"]
        else:
            if context.get("default_picking_type_code", False):
                return self.env["stock.picking.type"].search(
                    [("code", "=", context["default_picking_type_code"])], order="id"
                )[0]
            else:
                return False
