# -*- coding: utf-8 -*-
from odoo import api, models, fields
from urllib.parse import urlencode
from datetime import datetime , timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import pdb

def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')

def utcDate(self, ddate):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_date = local_tz.localize(ddate, is_dst=False)
	utc_date = local_date.astimezone(utc)
	return utc_date			

def localDate(self, utc_dt):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_dt = utc_dt.replace(tzinfo=utc).astimezone(local_tz)
	return local_dt	
	
class SalaryPlanner(models.Model):
	_inherit = 'wizard.planner'

	def _get_planner_application(self):
		planner = super(SalaryPlanner, self)._get_planner_application()
		planner.append(['planner_salary', 'Salary Planner'])
		return planner

	def _prepare_planner_salary_wizard(self,rec_id):
		#pdb.set_trace()
		ex_obj = self.env['hr.payslip.exception']
		company_slips = {}	
		company_contracts = {}
		
		values = {
			'company_id': self.env.user.company_id,
			'is_coa_installed': bool(self.env['account.account'].search_count([])),
			'payment_term': self.env['account.payment.term'].search([]),
			'supplier_menu_id': self.env.ref('account.menu_account_supplier').id
		}
		period = self.env['hr.payroll.period'].browse(rec_id)
		period_start_date = localDate(self,strToDatetime(period.date_start))
		period_end_date = localDate(self,strToDatetime(period.date_end))
		period_start_date_str = datetime.strftime(period_start_date,'%Y-%m-%d %H:%M')
		period_end_date_str = datetime.strftime(period_end_date,'%Y-%m-%d %H:%M')
		companies = self.env['res.company'].search([],order='id')
		slips = period.register_id.run_ids.mapped('slip_ids')
		
		if period.state == 'closed':
			contracts = period.register_id.run_ids.mapped('slip_ids').mapped('contract_id')
			employees = contracts.mapped('employee_id')					
			for company in companies:				
				company_slips[company.id] = { 'name':company.partner_id.code, 'slips':slips.filtered(lambda ct: ct.company_id.id == company.id) }
		else:
			contracts = period.schedule_id.contract_ids.filtered(lambda ct: ct.state == 'open')
			employees = period.schedule_id.contract_ids.mapped('employee_id')			
			for company in companies:
				company_contracts[company.id] = { 'name':company.partner_id.code, 'contracts':contracts.filtered(lambda ct: ct.company_id.id == company.id) }
				
		attendance_policy = self.env.user.company_id.attendance_policy
		if attendance_policy in ('bio_month','monthly'):
			attendance_ids = self.env['hr.employee.month.attendance'].search([('date','>=',period_start_date_str),('date','<=',period_end_date_str)])
		else:
			attendance_ids = self.env['hr.employee.month.attendance']
		
		input_ids = self.env['hr.salary.inputs'].search([('date','>=',period.date_start),('date','<=',period.date_end)])		
		holiday_ids = self.env['hr.holidays.public.line'].search([('date', '>=', period_start_date_str),('date', '<=', period_end_date_str),])	
		is_ended = period.is_ended()	
		locked = (period.state in ['locked', 'generate', 'payment', 'closed'])
		can_unlock = (period.state in ['locked', 'generate'])
		ps_generated = period.state in ['generate']
		payslips = period.register_id and True or False # (period.state in ['generate', 'payment', 'closed'] and period.register_id and True or False)
		payment_started = period.state in ['payment', 'closed']
		closed = period.state in ['closed']
		
		values.update({
			'period_start_date' : period_start_date_str[:10],
			'period_end_date' : period_end_date_str[:10],
			'period': period,
			'period_id': period.id,
			'alert_rule_ids': alert_rule_ids,
			'public_holiday_ids': holiday_ids,
			'is_ended': is_ended,
			'locked': locked,
			'can_unlock': can_unlock,
			'ps_generated': ps_generated,
			'slips': slips,
			'payslips': payslips,
			'payment_started': payment_started,
			'closed': closed,
			'attendance_policy': attendance_policy,
			'attendance_ids': attendance_ids,
			'input_ids': input_ids,
			'contracts': contracts,
			'companies': companies,
			'company_contracts': company_contracts,
			'company_slips': company_slips,
			'transfers': period.transfer_ids,
			
		})
		if period.register_id:
			slips = period.register_id.run_ids.mapped('slip_ids')
		return values
