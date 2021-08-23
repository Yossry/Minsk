# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.move"

    @api.multi
    def open_entry(self):
        view_id = self.env.ref("account.view_move_form").id
        return {
            "name": "Journal Entry",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "account.move",
            "view_id": view_id,
            "res_id": self.id,
            "target": "current",
            "type": "ir.actions.act_window",
        }
