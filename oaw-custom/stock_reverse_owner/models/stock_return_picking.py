# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    return_category = fields.Selection(
        [
            ("repair", "Repair"),
            ("return_company", "Return (Company)"),
            ("return_no_ownership_change", "Return (No Ownership Change)"),
        ],
        string="Return Category",
    )
    picking_id = fields.Many2one(
        "stock.picking",
        string="Picking",
        default=lambda self: self.env.context.get("active_id", False),
    )
    picking_type = fields.Selection(
        related="picking_id.picking_type_id.code", string="Picking Type"
    )

    @api.multi
    def _create_returns(self):
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env["stock.picking"].browse(new_picking_id)
        for rec in self:
            new_picking.return_category = rec.return_category
            if rec.return_category == "repair":
                new_picking.owner_id = new_picking.partner_id.id
            elif rec.return_category == "return_company":
                new_picking.owner_id = new_picking.company_id.partner_id.id
            # elif rec.return_category == 'return_vci':
            #     picking.owner_id = rec.supplier_id.id
            else:
                pass  # odoo standard case
        return new_picking_id, pick_type_id
