# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePrl(models.Model):

    _name = 'hr.employee.prl'
    _description = 'Hr Employee Prl'

    name = fields.Char(required=True)
    prl_date = fields.Date(string='Date', required=True)
    notes = fields.Text()
    employee_id = fields.Many2one('hr.employee')
