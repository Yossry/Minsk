# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventUpdate(models.TransientModel):
    _inherit = 'clv.event.updt'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsible Empĺoyee'
    )
    employee_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Responsible Empĺoyee', default=False, readonly=False, required=False
    )

    @api.multi
    def do_event_updt(self):
        self.ensure_one()

        super().do_event_updt()

        for event in self.event_ids:

            _logger.info(u'%s %s', '>>>>>', event.name)

            if self.employee_id_selection == 'set':
                event.employee_id = self.employee_id
            if self.employee_id_selection == 'remove':
                event.employee_id = False

        return True
