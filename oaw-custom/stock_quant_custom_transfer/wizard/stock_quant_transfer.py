# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class QuantTransferWizard(models.TransientModel):
    _name = "quant.transfer.wizard"

    location_dest_id = fields.Many2one(
        "stock.location", string="Destination Location", required=True
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type", string="Operation Type", required=True
    )
    sale_order_id = fields.Many2one("sale.order", string="Related Sales Order")

    @api.onchange("picking_type_id")
    def onchange_picking_type(self):
        location_domain = [("usage", "=", ("internal"))]
        if self.picking_type_id:
            if self.picking_type_id.default_location_dest_id:
                self.location_dest_id = self.picking_type_id.default_location_dest_id.id
            else:
                self.location_dest_id = self.env[
                    "stock.warehouse"
                ]._get_partner_locations()[0]
            if self.picking_type_id.code == "outgoing":
                location_domain = [("usage", "=", ("customer", "supplier"))]
        return {"domain": {"location_dest_id": location_domain}}

    @api.multi
    def action_stock_quant_transfer(self):
        context = dict(self._context or {})
        stock_quant_obj = self.env["stock.quant"]
        stock_move_obj = self.env["stock.move"]
        stock_picking_obj = self.env["stock.picking"]

        active_ids = context.get("active_ids", [])
        quant_ids = stock_quant_obj.browse(active_ids)
        source_location = quant_ids[0].location_id

        #  if selected quants are from different location then raise to
        #  avoid confusion of taking source location for picking
        if any(q.location_id != source_location for q in quant_ids):
            raise UserError(_("Please select quants that are in the same " "Location."))

        if source_location == self.location_dest_id:
            raise UserError(_("Please select different location to transfer."))

        # Check if any quants are already in any internal stock move,
        self.check_exist_stock_move_lines(quant_ids, source_location)

        # Get the picking type
        picking_type = self.picking_type_id

        origin_name = ",".join([q.display_name for q in quant_ids])

        #  prepare values for picking
        picking_vals = {
            "location_id": source_location.id,
            "picking_type_id": picking_type.id,
            "location_dest_id": self.location_dest_id.id,
            "origin": origin_name,
        }

        #  prepare moves
        picking_lines = []
        for quant in quant_ids:
            line_vals = {
                "product_id": quant.product_id.id,
                "product_uom_qty": quant.quantity,
                "picking_type_id": picking_type.id,
                "quant_id": quant.id,
                "lot_id": quant.lot_id.id,
            }
            if self.sale_order_id:
                line_vals["group_id"] = (
                    self.sale_order_id.procurement_group_id
                    and self.sale_order_id.procurement_group_id.id
                    or False
                )
            new_move = stock_move_obj.new(line_vals)
            new_move.onchange_product_id()
            move_dict = stock_move_obj._convert_to_write(
                {name: new_move[name] for name in new_move._cache}
            )
            picking_lines.append((0, 0, move_dict))

        picking_vals.update({"move_lines": picking_lines})
        picking_id = stock_picking_obj.create(picking_vals)

        for move in picking_id.move_lines:
            move._action_confirm(merge=False)
            move._recompute_state()

        action = self.env.ref("stock.action_picking_tree_all")
        action_vals = action.read()[0]
        action_vals["domain"] = str([("id", "=", picking_id.id)])
        return action_vals

    def check_exist_stock_move_lines(self, quant_ids, location_id):
        stock_move_line_obj = self.env["stock.move.line"]

        stock_move_line_list = stock_move_line_obj.search(
            [
                ("state", "not in", ["done", "cancel"]),
                ("location_id", "=", location_id.id),
                ("lot_id", "in", [q.id for q in quant_ids.mapped("lot_id")]),
            ]
        )
        if stock_move_line_list:
            error_msg = ""
            for stock_move in stock_move_line_list.mapped("move_id"):
                error_msg += "\n{}: {}".format(
                    stock_move.reference, stock_move.product_id.display_name
                )
            raise UserError(
                _(
                    "Some of the selected quants are being "
                    "processed by other internal Stock Move.\n"
                    "Please process the following Stock Moves "
                    "before creating new internal moves:%s"
                )
                % error_msg
            )
