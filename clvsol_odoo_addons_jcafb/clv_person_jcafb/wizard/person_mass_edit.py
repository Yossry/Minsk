# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonMassEdit(models.TransientModel):
    _inherit = 'clv.person.mass_edit'

    reg_state = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
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

    random_field = fields.Char(
        string='Random ID', default=False,
        help='Use "/" to get an automatic new Random ID.'
    )
    random_field_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Random ID:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_person_mass_edit(self):
        self.ensure_one()

        super().do_person_mass_edit()

        for person in self.person_ids:

            _logger.info(u'%s %s', '>>>>>', person.name)

            if self.reg_state_selection == 'set':
                person.reg_state = self.reg_state
            if self.reg_state_selection == 'remove':
                person.reg_state = False

            if self.state_selection == 'set':
                person.state = self.state
            if self.state_selection == 'remove':
                person.state = False

            if self.random_field_selection == 'set':
                person.random_field = self.random_field
            if self.random_field_selection == 'remove':
                person.random_field = False

        return True
