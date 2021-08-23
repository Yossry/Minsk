# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def _setup_base(self):
        init_res = super(Inventory, self)._setup_base()
        selection_add = ('ready', 'Waiting for Validation')
        if selection_add not in self._fields['state'].selection:
            # add new state 'ready' before 'done'
            self._fields['state'].selection.insert(-1, selection_add)
        return init_res

    @api.multi
    def finish_inventory(self):
        self.write({'state': 'ready'})
        return True

    @api.multi
    def return_inventory(self):
        self.write({'state': 'confirm'})
        return True
