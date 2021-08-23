# -*- coding: utf-8 -*-

from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    social_security_salary = fields.Float('Social Security Salary')
