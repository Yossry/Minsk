# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Employee(models.Model):
    _name = "hr.employee"
    _inherit = 'hr.employee', 'clv.abstract.code'

    code = fields.Char(string='Employee Code', required=False, default='/')
    code_sequence = fields.Char(default='hr.employee.code')
