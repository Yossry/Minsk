import pdb
import time

from datetime import datetime, timedelta
from dateutil import relativedelta

import itertools
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError

class attendance_action_reason(models.Model):
	_name = "attendance.action.reason"
	_description = "Action Reason"
	
	name = fields.Char('Reason', size=64, required=True, help='Specifie the reason.')


class hr_employee_month_attendance(models.Model):
	_name = "hr.employee.month.attendance"
	_description = "Month Attendance"
	_inherit = ['mail.thread']
	_order = 'id desc'

	date = fields.Date('Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10],track_visibility='always')
	employee_id = fields.Many2one('hr.employee', "Employee",track_visibility='always',required=True)
	state = fields.Selection([('draft','Draft'),('counted','Counted'),('done','Done')],'Status',default='draft')
	total_days = fields.Integer('Month Days',required=True,default=30)
	present_days = fields.Integer('Present Days',required=True,default=30)
	total_hours = fields.Integer('Total Hours')
	present_hours = fields.Integer('Present Hours')
	overtime_hours = fields.Integer('Overtime Hours')
	slip_id = fields.Many2one('hr.payslip', "Pay Slip")
	company_id = fields.Many2one('res.company','Company',related='employee_id.company_id',store=True)
	contract_id = fields.Many2one('hr.contract', "Contract")

	_sql_constraints = [
		('attendance_uniq', 'unique(date, employee_id,contract_id)', 'Attendance Date from Employee must be unique!'),
	]

	@api.multi
	def unlink(self):
		for rec in self:		
			if rec.slip_id and rec.slip_id.move_id:
				raise UserError(('You can not delete attendance of Employess for which Salary have been Finalized.'))
		return super(hr_employee_month_attendance, self).unlink()
		
	@api.multi
	def attendance_confirm(self):
		for rec in self:
			if rec.state == 'draft':
				rec.state = 'done'
				
	def daily_to_month(self, period_id):
		employee_ids = self.env['hr.employee']
		period = self.env['hr.payroll.period'].browse(period_id)
		employee_ids |= self.env['hr.attendance'].search([('check_in','>=',period.date_start),('check_in','<=',period.date_end)]).mapped('employee_id')			
		
		for employee in self.env['hr.employee'].search([]):
			if 'AEX' in employee.category_ids.mapped('name'):		
				employee_ids |= employee
		
		for employee in employee_ids:
			present_days = 30
			contract_id = False
			
			variation_ids = self.env['hr.employee.month.attendance.variations'].search([('period_id', '=', period.id),('employee_id', '=', employee.id),])
			
			if variation_ids:
				for variation_id in variation_ids:
					present_days = variation_id.days
					if variation_id.contract_id:
						contract_id = variation_id.contract_id and variation_id.contract_id.id or False
					
					absent_ids = self.env['hr.schedule.alert'].search([('name', '>=', period.date_start),('name', '<=', period.date_end),
					('absent', '=', True),('employee_id', '=', employee.id),])
					present_days -= len(absent_ids)
					
					if present_days > 0:
						rec = {
							'date': period.date_end,
							'employee_id': employee.id,
							'present_days': present_days,
							'contract_id' : contract_id or False,
						}
						self.create(rec)
			
			if not variation_ids:
				absent_ids = self.env['hr.schedule.alert'].search([('name', '>=', period.date_start),('name', '<=', period.date_end),
						('absent', '=', True),('employee_id', '=', employee.id),])
				present_days -= len(absent_ids)
				
				if present_days > 0:
					rec = {
						'date': period.date_end,
						'employee_id': employee.id,
						'present_days': present_days,
						'contract_id' : contract_id or False,
					}
					self.create(rec)			
	
		
class hr_employee_attendance(models.Model):
	_name = "hr.employee.attendance"
	_description = "Attendance"
	_inherit = ['mail.thread']
	_order = 'id desc'

	name = fields.Date('Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'),track_visibility='always')
	#project_id = fields.Many2one('servico.projects', required=True,string = 'Project')
	action = fields.Selection([('present', 'Present'), ('absent', 'Absent'), ('leave', 'Leave')], 'Action', required=True,track_visibility='always')
	action_desc = fields.Many2one("attendance.action.reason", "Action Reason", help='Specifie the reason.',track_visibility='always')
	employee_id = fields.Many2one('hr.employee', "Employee",track_visibility='always')
	state = fields.Selection([('draft','Draft'),('counted','Counted'),('done','Done')],'Status',track_visibility='onchange')
	slip_id = fields.Many2one('hr.payslip', "Pay Slip")

	@api.one	
	def unlink(self):		
		if self.slip_id and self.slip_id.move_id:
			raise UserError(('You can not delete attendance of Employess Days for which Salary have been Finalized.'))
	
	@api.multi
	def attendance_confirm(self):
		for rec in self:
			if rec.state == 'draft':
				rec.state = 'done'


class hr_employee(models.Model):
	_inherit = 'hr.employee'
	
	@api.one
	def _attendance_count(self):
		self.attendance_count = self.env['hr.employee.attendance'].search_count([('employee_id', '=', self.id),('slip_id', '=', False)])
		
	@api.one
	def _schedules_count(self):
		self.schedules_count = self.env['hr.schedule'].search_count([('employee_id', '=', self.id)])
		
	@api.multi
	def _month_attendance_count(self):
		for emp in self:
			month_total_days = month_att_days = 0
			#att_recs = self.env['hr.employee.month.attendance'].search([('employee_id', '=', emp.id),('date','=','2016-11-01')])
			att_recs = self.env['hr.employee.month.attendance'].search([('employee_id', '=', emp.id),('state','=','draft'),('slip_id','=',False)])
			for att_rec in att_recs:
				month_total_days += att_rec.total_days
				month_att_days += att_rec.present_days

			emp.month_total_days = month_total_days
			emp.month_att_days = month_att_days

	#Fields
	attendance_count = fields.Integer('Attendance Counts', compute='_attendance_count')
	month_total_days = fields.Integer('Month Days', compute='_month_attendance_count')
	month_att_days = fields.Integer('Present Days', compute='_month_attendance_count')
	schedules_count = fields.Integer('Contracts', compute='_schedules_count')


