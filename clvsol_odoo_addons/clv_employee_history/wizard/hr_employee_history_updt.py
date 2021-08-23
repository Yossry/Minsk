# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo import exceptions

_logger = logging.getLogger(__name__)


class EmployeeHistoryUpdate(models.TransientModel):
    _description = 'Employee History Update'
    _name = 'hr.employee.history_updt'

    def _default_employee_ids(self):
        return self._context.get('active_ids')
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='hr_employee_history_updt_rel',
        string='Employees',
        default=_default_employee_ids
    )
    date_sign_in = fields.Date(
        string='Sign in date',
        required=False,
    )
    date_sign_out = fields.Date(
        string="Sign out date",
        required=False
    )

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_employee_history_updt(self):
        self.ensure_one()

        HrEmployeeHistory = self.env['hr.employee.history']
        # HrJobHistory = self.env['hr.job.history']
        # HrDepartmentHistory = self.env['hr.department.history']

        for employee in self.employee_ids:

            if self.date_sign_out is False:
                raise exceptions.ValidationError('The "Sign out date" has not been defined!')
                return self._reopen_form()

            if self.date_sign_in is False:
                raise exceptions.ValidationError('The "Sign in date" has not been defined!')
                return self._reopen_form()

            _logger.info(u'%s %s', '>>>>>', employee.name)

            if employee.phase_id.id is not False:

                employee_history = HrEmployeeHistory.search([
                    ('employee_id', '=', employee.id),
                    ('phase_id', '=', employee.phase_id.id),
                    ('date_sign_out', '=', False),
                ])

                if employee_history.id is False:

                    employee_history_2 = HrEmployeeHistory.search([
                        ('employee_id', '=', employee.id),
                        ('date_sign_out', '=', False),
                    ])
                    if employee_history_2.id is not False:
                        employee_history_2.date_sign_out = self.date_sign_out
                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>', employee_history_2.phase_id.name,
                                                     employee_history_2.date_sign_in,
                                                     employee_history_2.date_sign_out)

                    values = {
                        'employee_id': employee.id,
                        'department_id': employee.department_id.id,
                        'job_id': employee.job_id.id,
                        'date_sign_in': self.date_sign_in,
                        'phase_id': employee.phase_id.id,
                    }
                    employee_history = HrEmployeeHistory.create(values)
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', employee_history.phase_id.name,
                                                 employee_history.date_sign_in,
                                                 employee_history.date_sign_out)

                else:
                    employee_history.job_id = employee.job_id.id
                    employee_history.department_id = employee.department_id.id
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', employee_history.phase_id.name,
                                                 employee_history.date_sign_in,
                                                 employee_history.date_sign_out)

            else:

                employee_history = HrEmployeeHistory.search([
                    ('employee_id', '=', employee.id),
                    ('date_sign_out', '=', False),
                ])

                if employee_history.id is not False:
                    employee_history.date_sign_out = self.date_sign_out
                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>', employee_history.phase_id.name,
                                                 employee_history.date_sign_in,
                                                 employee_history.date_sign_out)

        return True
        # return self._reopen_form()
