# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonAuxMassEdit(models.TransientModel):
    _inherit = 'clv.person_aux.mass_edit'

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
    def do_person_aux_mass_edit(self):
        self.ensure_one()

        super().do_person_aux_mass_edit()

        for person_aux in self.person_aux_ids:

            _logger.info(u'%s %s', '>>>>>', person_aux.name)

            if self.phase_id_selection == 'set':
                person_aux.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                person_aux.phase_id = False

        return True
