# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventMassEdit(models.TransientModel):
    _inherit = 'clv.event.mass_edit'

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
    def do_event_mass_edit(self):
        self.ensure_one()

        super().do_event_mass_edit()

        for event in self.event_ids:

            _logger.info(u'%s %s', '>>>>>', event.name)

            if self.phase_id_selection == 'set':
                event.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                event.phase_id = False

        return True
