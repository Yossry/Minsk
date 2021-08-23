# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FamilyAuxMassEdit(models.TransientModel):
    _inherit = 'clv.family_aux.mass_edit'

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
    def do_family_aux_mass_edit(self):
        self.ensure_one()

        super().do_family_aux_mass_edit()

        for family_aux in self.family_aux_ids:

            _logger.info(u'%s %s', '>>>>>', family_aux.name)

            if self.phase_id_selection == 'set':
                family_aux.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                family_aux.phase_id = False

        return True
