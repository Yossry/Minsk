# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_manager_id = fields.Many2one(
        'hr.employee', 'HR Manager')
    hr_pro_id = fields.Many2one(
        'hr.employee', 'QPR - PRO')
