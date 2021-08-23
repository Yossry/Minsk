# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sub_consigned = fields.Boolean("Sub Consigned")
    # For communication with warehouse group in Quotation List View
    prepare = fields.Boolean("Prepare")
    # Field for communication with Delivery Group in Quotation List View
    open_issue = fields.Boolean("Open Issue")
    # Field for communication with Delivery Group in Sales List View
    checked = fields.Boolean("Checked")
    state = fields.Selection(selection_add=[("done", "Done")])

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            order._update_order_line_sequence()
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        for order in res:
            order._update_order_line_sequence()
        return res

    def _update_order_line_sequence(self):
        order_lines = sorted(self.order_line, key=lambda r: (r.sequence, r.id))
        sequence = 1
        for order_line in order_lines:
            order_line.line_sequence = sequence
            sequence += 1

    @api.multi
    def action_open_order(self):
        view_id = self.env.ref("sale.view_order_form").id
        context = {}
        return {
            "name": "Sales Order",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "sale.order",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "context": context,
        }
