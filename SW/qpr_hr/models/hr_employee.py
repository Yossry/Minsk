# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    emp_seq = fields.Char("Employee Sequence",
                          required=True, copy=False, default='QPR')
    is_religious_leave_taken = fields.Boolean()

    @api.model
    def create(self, vals):
        if vals.get('emp_seq',  'QPR') == 'QPR':
            vals['emp_seq'] = self.env['ir.sequence'].next_by_code(
                'hr.employee') or 'QPR'
        return super(hr_employee, self).create(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['emp_seq'] = 'QPR'
        return super(hr_employee, self).copy(default=default)
