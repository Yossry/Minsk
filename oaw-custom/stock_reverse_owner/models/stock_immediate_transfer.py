# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    def process(self):
        for picking in self.pick_ids:
            if not picking._validate_owner("transfer"):
                raise UserError(
                    _(
                        "Owners are inconsistent between the picking \
                    and quant(s)."
                    )
                )
        return super(StockImmediateTransfer, self).process()
