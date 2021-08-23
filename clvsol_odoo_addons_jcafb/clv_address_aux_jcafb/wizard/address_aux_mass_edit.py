# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressAuxMassEdit(models.TransientModel):
    _inherit = 'clv.address_aux.mass_edit'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('verified', 'Verified'),
         ('ready', 'Ready'),
         ('done', 'Done'),
         ('canceled', 'Canceled')
         ], string='Register State', default=False, readonly=False, required=False
    )
    reg_state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='Register State:', default=False, readonly=False, required=False
    )

    state = fields.Selection(
        [('new', 'New'),
         ('available', 'Available'),
         ('waiting', 'Waiting'),
         ('selected', 'Selected'),
         ('unselected', 'Unselected'),
         ('unavailable', 'Unavailable'),
         ('unknown', 'Unknown')
         ], string='State', default=False, readonly=False, required=False
    )
    state_selection = fields.Selection(
        [('set', 'Set'),
         ], string='State:', default=False, readonly=False, required=False
    )

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsible Empĺoyee'
    )
    employee_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Responsible Empĺoyee:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_address_aux_mass_edit(self):
        self.ensure_one()

        super().do_address_aux_mass_edit()

        for address_aux in self.address_aux_ids:

            _logger.info(u'%s %s', '>>>>>', address_aux.name)

            if self.reg_state_selection == 'set':
                address_aux.reg_state = self.reg_state
            if self.reg_state_selection == 'remove':
                address_aux.reg_state = False

            if self.state_selection == 'set':
                address_aux.state = self.state
            if self.state_selection == 'remove':
                address_aux.state = False

            if self.employee_id_selection == 'set':
                address_aux.employee_id = self.employee_id
            if self.employee_id_selection == 'remove':
                address_aux.employee_id = False

        return True
