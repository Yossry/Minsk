# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class TripRequest(models.Model):
    _name = 'trip.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Trip Request'

    @api.model
    def _default_department_id(self):
        return self.env['hr.department'].search([('manager_id.user_id', '=', self.env.user.id)])

    @api.model
    def _default_ceo(self):
        return self.env['res.users'].search([('groups_id', 'in', [self.env.ref('qpr_crm.group_cxo').id])], limit=1)

    department_id = fields.Many2one('hr.department', string='Department', default=_default_department_id)
    manager_id = fields.Many2one(related='department_id.manager_id', string='Department Manager')
    ceo = fields.Many2one('res.users', string='CEO', default=_default_ceo)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    days = fields.Char(string='Business Trip Days')
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    trip_purpose = fields.Selection([
        ('work', 'Work'),
        ('training', 'Training'),
        ('conferece', 'Conference/Exhibition'),
        ('other', 'Other')], default='work')
    other_purpose = fields.Text(string='Other Purpose')
    budgeted = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes')
    cost = fields.Float(string='Accomodation Cost')
    dieam = fields.Float(string='Per Dieam')
    air_fare = fields.Float(string='Air Fare')
    other_allowence = fields.Char(string='Other Allowence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('approved_ceo', 'Approved by CEO'),
        ('rejected', 'Rejected')], string='Status', default='draft')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.activity_schedule(
            'qpr_hr.mail_act_trip_request_approval_employee',
            user_id=self.employee_id.user_id.id)
        return self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        self.ensure_one()
        if self.state == 'confirmed':
            self.activity_feedback(['qpr_hr.mail_act_trip_request_approval_employee'])
            self.activity_schedule(
                'qpr_hr.mail_act_trip_request_approval_ceo',
                user_id=self.ceo.id)
            self.state = 'approved'

        elif self.state == 'approved':
            self.activity_feedback(['qpr_hr.mail_act_trip_request_approval_ceo'])
            self.state = 'approved_ceo'
