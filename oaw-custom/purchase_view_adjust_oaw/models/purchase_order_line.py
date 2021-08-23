# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )
    line_sequence = fields.Integer(string="Sequence", readonly=True)
    move_state = fields.Selection(
        [
            ("draft", "New"),
            ("cancel", "Cancelled"),
            ("confirmed", "Waiting Availability"),
            ("assigned", "Available"),
            ("done", "Done"),
            ("na", "(N/A)"),
            ("multi", "(Multiple Statuses)"),
        ],
        compute="_get_move_state",
        store=True,
        readonly=True,
        copy=False,
        string="Move State",
    )

    @api.multi
    @api.depends("move_ids.state")
    def _get_move_state(self):
        for line in self:
            if line.move_ids:
                if all(m.state == "cancel" for m in line.move_ids):
                    line.move_state = "cancel"
                else:
                    state = ""
                    for m in line.move_ids:
                        if m.state == "cancel":
                            pass
                        elif state == "":
                            state = m.state
                        elif state != m.state:
                            state = "multi"
                    line.move_state = state
            else:
                line.move_state = "na"
