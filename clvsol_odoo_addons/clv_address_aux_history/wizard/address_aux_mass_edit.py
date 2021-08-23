# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddressAuxMassEdit(models.TransientModel):
    _inherit = 'clv.address_aux.mass_edit'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase'
    )
    phase_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Phase:', default=False, readonly=False, required=False
    )

    @api.multi
    def do_address_aux_mass_edit(self):
        self.ensure_one()

        super().do_address_aux_mass_edit()

        for address_aux in self.address_aux_ids:

            _logger.info(u'%s %s', '>>>>>', address_aux.name)

            if self.phase_id_selection == 'set':
                address_aux.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                address_aux.phase_id = False

        return True
