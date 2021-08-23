# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    users_to_notify_ot_ids = fields.Many2many('res.users', 'over_time_res_users_rel', string='Users To Notify') 
    overtime_type = fields.Selection([('request','Per Request'),('attendance','Based on Attendance')],default='request')
    overtime_analytic = fields.Selection([('with_entries','With Analytic Entries'),('without_entries','Without Analytic Entries')],default='with_entries')
    overtime_account_id = fields.Many2one('account.account',string="Overtime Expense Account")
    
    
    @api.multi
    def write(self, vals):
        res = super(ResCompany, self).write( vals)
        if vals.get('overtime_type',False) == 'attendance' and self.env.ref('base.module_hr_attendance').state != 'installed' :
            self.env.ref('base.module_hr_attendance').button_immediate_install()
            
        return res
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    users_to_notify_ot_ids = fields.Many2many('res.users', string='Users To Notify', related="company_id.users_to_notify_ot_ids",readonly=False) 
    overtime_type = fields.Selection([('request','Per Request'),('attendance','Based on Attendance')],default='request',related='company_id.overtime_type',readonly=False)
    overtime_analytic = fields.Selection([('with_entries','With Analytic Entries'),('without_entries','Without Analytic Entries')],default='with_entries',related='company_id.overtime_analytic',readonly=False)
    overtime_account_id = fields.Many2one('account.account',string="Overtime Expense Account",related="company_id.overtime_account_id",readonly=False)