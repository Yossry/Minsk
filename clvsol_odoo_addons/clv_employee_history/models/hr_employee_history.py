# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import *

from odoo import fields, models


class EmployeeHistory(models.Model):
    _description = 'Employee History'
    _name = 'hr.employee.history'
    _order = "date_sign_in desc"

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        required=False
    )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job',
        required=False
    )
    date_sign_in = fields.Date(
        string='Sign in date',
        required=False,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d')
    )
    date_sign_out = fields.Date(
        string="Sign out date",
        required=False
    )

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_history_ids = fields.One2many(
        comodel_name='hr.employee.history',
        inverse_name='employee_id',
        string='Employee History'
    )
