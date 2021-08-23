# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_manager_id = fields.Many2one(
        'hr.employee', 'HR Manager',
        related='company_id.hr_manager_id', readonly=False)
    hr_pro_id = fields.Many2one(
        'hr.employee', 'QPR - PRO',
        related='company_id.hr_pro_id', readonly=False)
