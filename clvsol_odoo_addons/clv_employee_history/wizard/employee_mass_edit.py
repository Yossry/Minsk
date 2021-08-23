# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EmployeeMassEdit(models.TransientModel):
    _inherit = 'hr.employee.mass_edit'

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
    def do_employee_mass_edit(self):
        self.ensure_one()

        super().do_employee_mass_edit()

        for employee in self.employee_ids:

            _logger.info(u'%s %s', '>>>>>', employee.name)

            if self.phase_id_selection == 'set':
                employee.phase_id = self.phase_id
            if self.phase_id_selection == 'remove':
                employee.phase_id = False

        return True
