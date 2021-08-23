# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    employee_ids = fields.One2many(
        comodel_name='hr.employee',
        inverse_name='phase_id',
        string='Employees',
        readonly=True
    )
    count_employees = fields.Integer(
        string='Employees (count)',
        compute='_compute_employee_ids_and_count',
    )

    @api.multi
    def _compute_employee_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            employees = self.env['hr.employee'].search(search_domain)

            record.count_employees = len(employees)
            record.employee_ids = [(6, 0, employees.ids)]


class Employee(models.Model):
    _inherit = 'hr.employee'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )


class EmployeeHistory(models.Model):
    _inherit = 'hr.employee.history'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )
