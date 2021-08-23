# -*- coding: utf-8 -*-

from datetime import date, datetime, time
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class HRLeaveRestriction(models.Model):
    _name = 'hr.leave.restriction'
    _description = 'Leave Restriction'

    name = fields.Char()
    period_ids = fields.One2many('leave.restriction.period', 'restriction_id', string='Restriction Period')
    active = fields.Boolean(default=True)


class LeaveRestrictionPeriod(models.Model):
    _name = 'leave.restriction.period'
    _description = 'Restriction Period'

    restriction_id = fields.Many2one('hr.leave.restriction')
    name = fields.Char('Description')
    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')


class HRLeave(models.Model):
    _inherit = 'hr.leave'
    _order = "reference desc"

    exit_permit = fields.Boolean(string="Need Exit Permit?")
    current_country = fields.Char(string="Country During Leave")
    air_ticket = fields.Boolean(related='holiday_status_id.air_ticket')
    is_employee = fields.Boolean(compute='_compute_is_employee')
    air_ticket_count = fields.Integer(compute='_compute_air_ticket_count')
    reference = fields.Char()
    leaves_count = fields.Float(related='employee_id.leaves_count')
    note = fields.Text()
    phone_during_leave = fields.Char(related='employee_id.mobile_phone', readonly=True, string='Contact No.')
    phone_during_leave1 = fields.Char(string="Other Contact No", help='Contact number during the leave period')
    illness_type = fields.Char(string="Illness Type", help="Mention about your sickness in brief, if taking sick leave")
    is_sick_leave = fields.Boolean(related='holiday_status_id.is_sick_leave')

    @api.constrains('date_from', 'date_to')
    def _check_restriction_leave(self):
        restriction = self.env['hr.leave.restriction'].search([], limit=1)
        periods = restriction.period_ids
        for period in periods:
            for holiday in self:
                if holiday.date_to >= period.date_from and holiday.date_from <= period.date_to:
                    raise ValidationError(_('You can not create a leave on restrcition day!'))

    @api.constrains('holiday_status_id')
    def check_religious_leave(self):
        for leave in self:
            if leave.holiday_status_id.is_religious and leave.employee_id.is_religious_leave_taken:
                raise ValidationError(_('You already have took the Religious Leave.'))

    @api.multi
    def _compute_is_employee(self):
        is_office = self.env.user.has_group('hr.group_hr_user')
        is_manager = self.env.user.has_group('hr.group_hr_manager')
        for leave in self:
            if not is_manager and not is_office:
                leave.is_employee = True

    @api.multi
    def _compute_air_ticket_count(self):
        AirTicket = self.env['air.ticket.request']
        for leave in self:
            leave.air_ticket_count = AirTicket.search_count([('leave_id', '=', leave.id)])

    @api.multi
    def action_generate_air_ticket_request(self):
        action = self.env.ref('qpr_hr.action_air_ticket_request')
        result = action.read()[0]
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_leave_id': self.id,
            'default_employee_id': self.employee_id.id,
            'default_leave_type_id': self.holiday_status_id.id,
            'default_name': self.note,
        }
        res = self.env.ref('qpr_hr.air_ticket_request_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = False
        return result

    @api.multi
    def action_view_leave(self):
        action = self.env.ref('hr_holidays.act_hr_employee_holiday_request')
        result = action.read()[0]
        result['context'] = {
            'search_default_employee_id': self.employee_id.ids,
            'default_employee_id': self.employee_id.id,
            'search_default_group_type': 1,
            'search_default_year': 1
        }
        return result

    @api.multi
    def action_confirm(self):
        if not self.env.context.get('attachment_warning') and self.holiday_status_id.attachment_required and (self.holiday_status_id.attachment_required_days < self.number_of_days_display):
            if not self.env['ir.attachment'].search_count([('res_model', '=', self._name), ('res_id', '=', self.id)]):
                return {
                    'name': _('Attachment Warning'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.leave.warning',
                    'view_id': self.env.ref('qpr_hr.hr_leave_warning_view').id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        return super(HRLeave, self).action_confirm()

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('hr.leave')
        vals['name'] = vals['reference']
        if vals.get('holiday_status_id'):
            leave_type = self.env['hr.leave.type'].browse(vals['holiday_status_id'])
            if leave_type.attachment_required and leave_type.attachment_required_days < vals.get('number_of_days', 0):
                vals['state'] = 'draft'
            if leave_type.is_religious:
                self.env['hr.employee'].browse(vals['employee_id']).sudo().write({'is_religious_leave_taken': True})
        res = super(HRLeave, self).create(vals)
        return res

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if employee_id and self.holiday_status_id.exclude_weekly_holiday and self.holiday_status_id.resource_calendar_id:
            employee = self.env['hr.employee'].browse(employee_id)
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
            return employee.get_work_days_data(day_from, day_to, calendar=self.holiday_status_id.resource_calendar_id)['days']
        return super(HRLeave, self)._get_number_of_days(date_from, date_to, employee_id)

    def _get_responsible_for_approval(self):
        company_id = self.department_id.company_id
        if self.state == 'validate1' and company_id.hr_manager_id.user_id:
            return company_id.hr_manager_id.user_id
        return super(HRLeave, self)._get_responsible_for_approval()

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        department_id = self.env['hr.department'].search([('manager_id', '=', current_employee.id)], limit=1)
        is_department_manager = self.env.user.has_group('qpr_hr.group_department_manager')
        call_super = True
        for leave in self:
            if state in ['validate1', 'refuse', 'validate'] and is_department_manager and leave.department_id.id == department_id.id:
                call_super = False
        if call_super:
            super(HRLeave, self)._check_approval_update(state)


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    air_ticket_ids = fields.One2many('air.ticket.request', 'leave_type_id', string='Air Ticket Requests')
    air_ticket_counts = fields.Integer(compute='_count_air_tickets')
    air_ticket = fields.Boolean('Allowed Air ticket', default=False,
                                help="If this leave type allow employee to have an option for Air Ticket Request")
    no_of_ticket_allowed = fields.Integer(
        default=1, string='Maximum Time Ticket Allowed', help="Maximum No. of ticket allowed on this leave type")
    attachment_required = fields.Boolean('Attachment Required')
    attachment_required_days = fields.Integer(
        default=2, string='Days After', help="Attachment required Beyond a particular defined days")
    exclude_weekly_holiday = fields.Boolean(string='Exclude Weekly Holidays', default=False)
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours')
    is_religious = fields.Boolean(string='Is Religious')
    is_sick_leave = fields.Boolean(string='Sick Leave')

    @api.multi
    @api.depends('air_ticket_ids', 'no_of_ticket_allowed')
    def _count_air_tickets(self):
        for lt in self:
            lt.air_ticket_counts = len(lt.air_ticket_ids.ids)
