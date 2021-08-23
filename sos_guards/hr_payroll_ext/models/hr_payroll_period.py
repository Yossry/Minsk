import pdb
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import common_timezones, timezone, utc

from odoo.tools.safe_eval import safe_eval as eval
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OEDATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')


def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')

def dateToStr(ddate):
	return ddate.strftime('%Y-%m-%d')
	
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

def parse_date(td):
	resYear = float(td.days)/365.0                  
	resMonth = (resYear - int(resYear))*365.0/30.0 
	resDays = int((resMonth - int(resMonth))*30)
	resYear = int(resYear)
	resMonth = int(resMonth)
	return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")

def compute_duration(ddate):
	start = datetime.strptime(ddate,OEDATE_FORMAT)
	end = datetime.strptime(time.strftime(OEDATE_FORMAT),OEDATE_FORMAT)	
	delta = end - start
	return parse_date(delta)

def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	#year = sourcedate.year + month / 12
	year = sourcedate.year
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year, month)[1])
	return datetime(year, month, day)


class account_move(models.Model):
	_inherit = 'account.move'
	
	period_id = fields.Many2one('hr.payroll.period')


class hr_payroll_period(models.Model):
	_name = 'hr.payroll.period'
	_inherit = ['mail.thread']
	_order = "date_start, name desc"

	name = fields.Char('Description', size=256, required=True)
	schedule_id = fields.Many2one('hr.payroll.period.schedule', 'Payroll Period Schedule',required=True)
	date_start = fields.Datetime('Start Date', required=True)
	date_end = fields.Datetime('End Date', required=True)
	register_id = fields.Many2one('hr.payroll.register', 'Payroll Register', readonly=True,states={'generate': [('readonly', False)]})
	transfer_ids = fields.One2many('account.move','period_id')
	state = fields.Selection([('open', 'Open'),('ended', 'End of Period Processing'),('locked', 'Locked'),('unlocked', 'Un-Locked'),('generate', 'Generating Payslips'),
		('payment', 'Payment'),('closed', 'Closed')],'State', index=True, readonly=True,default='open')
	overtime_posted = fields.Boolean("Overtime Posted", default=False)	

	_track = {
		'state': {
			'hr_payroll_period.mt_state_open': (lambda self, obj: obj['state'] == 'open'),
			'hr_payroll_period.mt_state_end': (lambda self, obj: obj['state'] == 'ended'),
			'hr_payroll_period.mt_state_lock': (lambda self, obj: obj['state'] == 'locked'),
			'hr_payroll_period.mt_state_generate': (lambda self, obj: obj['state'] == 'generate'),
			'hr_payroll_period.mt_state_payment': (lambda self, obj: obj['state'] == 'payment'),
			'hr_payroll_period.mt_state_close': (lambda self, obj: obj['state'] == 'closed'),
		},
	}

	@api.model
	def create(self,vals):
		period = super(hr_payroll_period, self).create(vals)
		data = {
			'name': 'Salary Planner',
			'planner_application': 'planner_salary',
			'view_id': 1161,
			'active': True,
			'tooltip_planner': '<p>Salary Processing: a step-by-step guide.</p>',
			'rec_model': 'hr.payroll.period',
			'rec_id': period.id,
		}
		
		self.env['wizard.planner'].create(data);
		return period

	@api.one
	def is_ended(self):
		flag = False
		utc_tz = timezone('UTC')
		utcDtNow = utc_tz.localize(datetime.now(), is_dst=False)
		
		dtEnd = datetime.strptime(self.date_end, '%Y-%m-%d %H:%M:%S')
		utcDtEnd = utc_tz.localize(dtEnd, is_dst=False)
		if utcDtNow > utcDtEnd + timedelta(minutes=(self.schedule_id.ot_max_rollover_hours * 60)):
			flag = True
		return flag

	@api.multi
	def try_signal_end_period(self):
		"""Method called, usually by cron, to transition any payroll periods that are past their end date."""
		utc_tz = timezone('UTC')
		utcDtNow = utc_tz.localize(datetime.now(), is_dst=False)
		period_ids = self.search([('state', 'in', ['open']),('date_end', '<=', utcDtNow.strftime('%Y-%m-%d %H:%M:%S')),])
		if period_ids:
			period_ids.set_state_ended()

	@api.multi
	def create_payslip_runs(self, register, dept_ids, contracts, tz):
		contract_obj = self.env['hr.contract']
		slip_obj = self.env['hr.payslip']

		# DateTime in db is store as naive UTC. Convert it to explicit UTC and then convert that into the time zone of the pay period schedule.
		loclDTStart = localDate(self,strToDatetime(self.date_start))
		date_start = dateToStr(loclDTStart)
		loclDTEnd = localDate(self,strToDatetime(self.date_end))
		date_end = dateToStr(loclDTEnd)

		# Get Pay Slip Amendments, Employee ID, and the amount of the amendment
		psa_codes = []
		psa_ids = self._get_confirmed_amendments()
		for psa in self.env['hr.payslip.amendment'].browse(psa_ids):
			psa_codes.append((psa.employee_id.id, psa.input_id.code, psa.amount))

		# Keep track of employees that have already been included
		seen_ee_ids = []

		# Create payslip batch (run) for each department
		for dept in dept_ids:
			#c_ids = contract_obj.search([('id', 'in', contracts.ids),'|',('department_id.id', '=', dept.id),('employee_id.department_id.id', '=', dept.id)])
			#c2_ids = contract_obj.search([('id', 'in', contracts.ids),'|',('job_id.department_id.id', '=', dept.id),('end_job_id.department_id.id', '=', dept.id),])
			#d_contracts = c_ids | c2_ids
			
			c_ids = contract_obj.search([('id', 'in', contracts.ids),('department_id.id', '=', dept.id)])
			d_contracts = c_ids
			
			if len(d_contracts) == 0:
				continue

			run_res = {
				'name': dept.short_name,
				'date_start': date_start,
				'date_end': date_end,
				'register_id': register.id,
			}
			run = self.env['hr.payslip.run'].create(run_res)

			# Create a pay slip for each employee in each department that has a contract in the pay period schedule of this pay period
			slip_ids = self.env['hr.payslip']
			
			for contract in d_contracts:
				
				# Does employee have a contract in this pay period?
				dContractStart = datetime.strptime(contract.date_start, OEDATE_FORMAT).date()
				dContractEnd = loclDTEnd.date()
				if contract.date_end:
					dContractEnd = datetime.strptime(contract.date_end, OEDATE_FORMAT).date()
				if (dContractStart > loclDTEnd.date() or dContractEnd < loclDTStart.date()):
					continue

				# If the contract doesn't cover the full pay period use the contract dates as start/end dates instead of the full period.
				#
				temp_date_start = date_start
				temp_date_end = date_end
				if dContractStart > datetime.strptime(date_start, OEDATE_FORMAT).date():
					temp_date_start = dContractStart.strftime(OEDATE_FORMAT)
				if (contract.date_end and dContractEnd < datetime.strptime(date_end, OEDATE_FORMAT).date()):
					temp_date_end = dContractEnd.strftime(OEDATE_FORMAT)
					
				slip_data = slip_obj.onchange_employee_id(temp_date_start, temp_date_end, employee_id=contract.employee_id.id, contract_id=contract.id)

				# Make modifications to rule inputs
				for line in slip_data['value'].get('input_line_ids', False):
					# Pay Slip Amendment modifications
					for eid, code, amount in psa_codes:
						if eid == contract.employee_id.id and line['code'] == code:
							line['amount'] = amount
							break
							
				#If Month attendance Entry Found 			
				if (slip_data['value'].get('worked_days_line_ids', False)):
					res = {
						'employee_id': contract.employee_id.id,
						'name': slip_data['value'].get('name', False),
						'struct_id': slip_data['value'].get('struct_id', False),
						'contract_id': slip_data['value'].get('contract_id', False),
						'payslip_run_id': run.id,
						'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
						'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
						'date_from': date_start,
						'date_to': date_end,
						'journal_id': contract.journal_id.id,
					}
					slip_ids |= slip_obj.create(res)
				
			# Calculate payroll for all the pay slips in this batch (run)
			#slip_ids.compute_sheet()
			for slip in slip_ids:
				# Here two lines, First code MAX and Second Code WORK100 so we checked the WORKED 100
				if slip.worked_days_line_ids and slip.worked_days_line_ids[1].number_of_days > 0.0:
					slip.compute_sheet()
		return
		
	@api.multi
	def create_payroll_register(self):
		if self.state not in ['locked', 'generate']:
			raise UserError(_('Invalid Action\n You must lock the Payroll Period first.'))
			
		# Remove any pre-existing payroll registers
		for register in self.register_id:
			for run in register.run_ids:
				run.slip_ids.unlink()
				run.unlink()
			register.unlink()
		
		
		# Create the payroll register
		register = self.env['hr.payroll.register'].create({
			'name': self.name + ': Register',
			'date_start': self.date_start,
			'date_end': self.date_end,
		})

		# Get list of departments and list of contracts for this period's schedule
		department_ids = self.env['hr.department'].search([('company_id', '=', register.company_id.id)])
		
		# Create payslips for employees, in all departments, that have a contract in this pay period's schedule
		self.create_payslip_runs(register, department_ids, self.schedule_id.contract_ids, self.schedule_id.tz)

		# Attach payroll register to this pay period
		self.register_id = register.id

		# Trigger re-calculation of exact change
		#self._change_res['done'] = False

		# Mark the pay period as being in the payroll generation stage
		self.state = 'generate'

		# return Payslips window here
		return {
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.payroll.register',
			'type': 'ir.actions.act_window',
			'views': [[False, 'list'], [False, 'form']],
			'res_id': register.id,
			#'domain': [['employee_id', 'in', employee_ids],['name', '>=', self.date_start],['name', '<=', self.date_end],['severity','in',['high','critical']]],			
			#'context': self._context
		}
		
	@api.multi
	def set_state_ended(self):
		attendance_obj = self.env['hr.attendance']
		detail_obj = self.env['hr.schedule.detail']
		holiday_obj = self.env['hr.leave']

		for period in self:
			utcDtStart = utcDate(self,strToDatetime(period.date_start))
			utcDtEnd = utcDate(self,strToDatetime(period.date_end))
	
			if period.state in ['locked', 'generate']:
				for contract in period.schedule_id.contract_ids:
					employee = contract.employee_id

					# Unlock attendance
					punch_ids = attendance_obj.search([('employee_id', '=', employee.id),
						('check_in', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('check_out', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='check_in')
					punch_ids.signal_unlock()

					# Unlock schedules
					detail_ids = detail_obj.search([('schedule_id.employee_id', '=', employee.id),
						('date_start', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('date_start', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='date_start')
					detail_ids.signal_unlock()

					# Unlock holidays/leaves that end in the current period
					holiday_ids = holiday_obj.search([('employee_id', '=', employee.id),
						('date_to', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('date_to', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),])
					
					holiday_ids.write({'payroll_period_state': 'unlocked'})

			period.write({'state': 'ended'})

	@api.multi
	def set_state_locked(self):
		attendance_obj = self.env['hr.attendance']
		detail_obj = self.env['hr.schedule.detail']
		holiday_obj = self.env['hr.leave']
		for period in self:
			utc_tz = timezone('UTC')
			dt = datetime.strptime(period.date_start, '%Y-%m-%d %H:%M:%S')
			utcDtStart = utc_tz.localize(dt, is_dst=False)
			dt = datetime.strptime(period.date_end, '%Y-%m-%d %H:%M:%S')
			utcDtEnd = utc_tz.localize(dt, is_dst=False)
			for contract in period.schedule_id.contract_ids:
				employee = contract.employee_id

				# Lock sign-in and sign-out attendance records
				punch_ids = attendance_obj.search([('employee_id', '=', employee.id),
					('check_in', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('check_out', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='check_in')
				punch_ids.sudo().write({'state':'locked'})
				
				# Lock schedules
				detail_ids = detail_obj.search([('schedule_id.employee_id', '=', employee.id),
					('hour_from', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('hour_from', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='hour_from')
				
				detail_ids.write({'state':'locked'})
				
				# Lock holidays/leaves that end in the current period
				holiday_ids = holiday_obj.search([('employee_id', '=', employee.id),
					('date_to', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('date_to', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),])
				
				if holiday_ids:
					for holiday_id in holiday_ids:
						holiday_id.write({'payroll_period_state': 'locked'})

			period.write({'state': 'locked'})

		return True

	@api.multi
	def set_state_unlocked(self):
		attendance_obj = self.env['hr.attendance']
		detail_obj = self.env['hr.schedule.detail']
		holiday_obj = self.env['hr.leave']
		for period in self:
			utc_tz = timezone('UTC')
			dt = datetime.strptime(period.date_start, '%Y-%m-%d %H:%M:%S')
			utcDtStart = utc_tz.localize(dt, is_dst=False)
			dt = datetime.strptime(period.date_end, '%Y-%m-%d %H:%M:%S')
			utcDtEnd = utc_tz.localize(dt, is_dst=False)
			
			#if self.state == 'generate':
			#	for run in self.register_id.run_ids:
			#		run.slip_ids.unlink()
			#		run.unlink()
			#	self.register_id.unlink()
				
			for contract in period.schedule_id.contract_ids:
				employee = contract.employee_id

				# UnLock sign-in and sign-out attendance records
				punch_ids = attendance_obj.search([('employee_id', '=', employee.id),
					('check_in', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('check_out', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='check_in')
				punch_ids.sudo().write({'state':'unlocked'})
				
				
				# UnLock schedules
				detail_ids = detail_obj.search([('schedule_id.employee_id', '=', employee.id),
					('hour_from', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('hour_from', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),], order='hour_from')
				
				detail_ids.write({'state':'unlocked'})
				

				# Lock holidays/leaves that end in the current period
				holiday_ids = holiday_obj.search([('employee_id', '=', employee.id),
					('date_to', '>=', utcDtStart.strftime('%Y-%m-%d %H:%M:%S')),('date_to', '<=', utcDtEnd.strftime('%Y-%m-%d %H:%M:%S')),])
				
				if holiday_ids:
					for holiday_id in holiday_ids:
						holiday_id.write({'payroll_period_state': 'unlocked'})

			period.write({'state': 'unlocked'})
			
	@api.multi
	def _get_confirmed_amendments(self):
		psa_ids = self.env['hr.payslip.amendment'].search([('pay_period_id', '=', self.id),('state', 'in', ['validate']),])
		return psa_ids

	@api.multi
	def _get_draft_amendments(self):
		psa_ids = self.env['hr.payslip.amendment'].search([('pay_period_id', '=', self.id),('state', 'in', ['draft']),])
		return psa_ids

	@api.multi
	def do_recalc_alerts(self):
		employees = []
		[employees.append(c.employee_id) for c in self.schedule_id.contract_ids]

		dtStart = datetime.strptime(self.date_start, '%Y-%m-%d %H:%M:%S')
		dtEnd = datetime.strptime(self.date_end, '%Y-%m-%d %H:%M:%S')

		dtNext = dtStart
		while dtNext <= dtEnd:
			for employee in employees:
				self.env['hr.schedule.alert'].compute_alerts_by_employee(employee,dtNext.date().strftime('%Y-%m-%d'))
			dtNext += relativedelta(days=+1)
	
	@api.multi
	def inter_transfer_salary(self):
		companies = [3,4,5,6]
		journals = {3:38, 4:43, 5:42, 6:44}

		for company in companies:
			self.transfer_salary_1(company,journals.get(company))
		for company in companies:
			self.transfer_salary_2(company,journals.get(company))

			
	@api.multi
	def view_contracts(self):
		abc = {
			'name': self.schedule_id.name,
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.payroll.period.schedule',
			'views': [[False, 'form']],			
			'res_id': self.schedule_id.id,			
		}		
		return abc
		
	@api.multi
	def view_contracts2(self):
	
		view_id = self.env['ir.ui.view'].search([('name','=','hr.payperiod.contract.tree')]).id
		abc = {
			'name': self.schedule_id.name + '-Contracts',
			'type': 'ir.actions.act_window',
			'view_type': 'tree',
			'view_mode': 'tree',
			'res_model': 'hr.contract',
			'views': [[view_id, 'list']],
			'domain': [['id', 'in', self.schedule_id.contract_ids.ids]],			
		}		
		return abc
			
	@api.multi
	def view_inter_transfer(self):	
		
		abc = {
			'name': 'Inter Company Salary Transfers',
			'type': 'ir.actions.act_window',
			'view_type': 'tree',
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'views': [[False, 'list'], [False, 'form']],
			'domain': [['id', 'in', self.transfer_ids.ids]],			
		}		
		return abc
		
	@api.multi
	def view_alerts(self):
		employee_ids = []
		[employee_ids.append(c.employee_id.id) for c in self.schedule_id.contract_ids]
	
		abc = {
			'name': 'Exception Alerts',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.schedule.alert',
			'views': [[False, 'list'], [False, 'form']],
			#'res_id': 1,
			'context': {'search_default_critical_f':1,'search_default_high_f':1},
			'domain': [['employee_id', 'in', employee_ids],['name', '>=', self.date_start],['name', '<=', self.date_end],['severity','in',['high','critical']]],			
		}		
		return abc
	
	@api.multi
	def view_payroll_register(self):		
		return {
			'name': 'Salary Registers',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.payroll.register',
			'views': [[False, 'list'], [False, 'form']],
			'res_id': self.register_id.id,
			'type': 'ir.actions.act_window',
			'context': self._context,
		}

	@api.multi
	def view_payroll_batch(self):
		return {
			'name': 'Payslip Batches',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.payslip.run',
			'views': [[False, 'list'], [False, 'form']],
			'domain': [['register_id', '=', self.register_id.id]],	
			'type': 'ir.actions.act_window',
			'context': self._context,
		}

	@api.multi
	def view_payslips(self):
		return {
			'name': 'Payslips',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.payslip',
			'views': [[False, 'list'], [False, 'form']],
			'domain': [['id', 'in', self.register_id.run_ids.mapped('slip_ids').ids]],	
			'type': 'ir.actions.act_window',
			'context': self._context,
		}
		
	@api.multi
	def view_monthly_attendance(self):
		employee_ids = []
		[employee_ids.append(c.employee_id.id) for c in self.schedule_id.contract_ids]
		
		start_date = localDate(self,strToDatetime(self.date_start))
		end_date = localDate(self,strToDatetime(self.date_end))
		start_date_str = datetime.strftime(start_date,'%Y-%m-%d %H:%M')
		end_date_str = datetime.strftime(end_date,'%Y-%m-%d %H:%M')
		
		abc = {
			'name': 'Monthly Attendance',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.employee.month.attendance',
			'views': [[False, 'list'], [False, 'form']],
			#'res_id': 1,
			#'context': {'search_default_critical_f':1,'search_default_high_f':1},
			'domain': [['date', '>=', start_date_str],['date', '<=', end_date_str],],	# ['employee_id', 'in', employee_ids],		
		}		
		return abc
	
	@api.multi
	def view_monthly_inputs(self):
		employee_ids = []
		[employee_ids.append(c.employee_id.id) for c in self.schedule_id.contract_ids]
		
		start_date = localDate(self,strToDatetime(self.date_start))
		end_date = localDate(self,strToDatetime(self.date_end))
		
		overtime_start_date = start_date + relativedelta(months=-1,day=21)
		overtime_end_date = start_date + relativedelta(day=21,minutes=-1)
		
		start_date_str = datetime.strftime(overtime_start_date,'%Y-%m-%d %H:%M')
		end_date_str = datetime.strftime(overtime_end_date,'%Y-%m-%d %H:%M')
		
		abc = {
			'name': 'Salary Adjustments',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.salary.inputs',
			'views': [[False, 'list'], [False, 'form']],
			#'res_id': 1,
			#'context': {'search_default_critical_f':1,'search_default_high_f':1},
			#'domain': [['date', '>=', start_date_str],['date', '<=', end_date_str],],	# ['employee_id', 'in', employee_ids],
			'domain': [['date', '>=', self.date_start],['date', '<=', self.date_end],],		
		}		
		return abc
		
	@api.multi	
	def view_payroll_exceptions(self):
		slip_ids = self.register_id.run_ids.mapped('slip_ids').ids

		abc = {
			'name': 'Payslip Exceptions',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.payslip.exception',
			'views': [[False, 'list'], [False, 'form']],			
			#'context': {'search_default_critical_f':1,'search_default_high_f':1},
			'domain': [['slip_id', 'in', slip_ids]],
		}		
		return abc
	
	@api.multi	
	def start_payments(self):
		# Set Pay Slip Amendments to Done #
		psa_ids = self._get_confirmed_amendments()
		psa_ids.write({'state':'done'})

		# Verify Pay Slips	#
		slips =  self.register_id.run_ids.mapped('slip_ids')
		#slips.action_payslip_done()
		slips.write({'state':'done'})
			
		self.state = 'payment'

	@api.multi
	def summary_payslips(self):		
		return {
			'name': 'Payslips Summary',
			'type': 'ir.actions.act_window',
			'view_type': 'pivot',
			'view_mode': 'pivot',
			'res_model': 'hr.payslip.line',
			'views': [[False, 'pivot']],			
			#'context': {'search_default_critical_f':1,'search_default_high_f':1},
			#'domain': [['slip_id', 'in', slip_ids]],
		}
		
	@api.multi
	def print_payroll_summary(self):				
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr.payroll.register.summary',
			'datas': {'ids': [self.register_id.id]},
		}
		
	@api.multi
	def print_payroll_register(self):		
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_register_report',
			'datas': {'ids': [self.register_id.id]},
		}
	
	@api.multi
	def print_payslip_details(self):		
		slip_ids = []
		for run in self.register_id.run_ids:
			[slip_ids.append(s.id) for s in run.slip_ids]

		return {
			'type': 'ir.actions.report',
			'report_name': 'payslip',
			'datas': {'ids': slip_ids},
		}
		
	@api.multi
	def print_contribution_registers(self):				
		
		register_ids = self.env['hr.contribution.register'].search([]).ids

		form = {
			'date_from': self.date_start,
			'date_to': self.date_end,
		}
		
		return {
			'type': 'ir.actions.report',
			'report_name': 'contribution.register.lines',
			'datas': {
				'ids': register_ids, 'form': form,
				'model': 'hr.contribution.register'},
		}
	
	@api.multi
	def print_payroll_sheet_1(self):			
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 1,
			'register_id': self.register_id.id
		}
		return self.env.ref('hr_payroll_ext.report_salary_sheet').report_action([], data=data, config=False)		
			
	@api.multi
	def print_payroll_sheet_3(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 3,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salarysheet',
			'datas': data,
		}		
		
	@api.multi
	def print_payroll_sheet_4(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 4,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salarysheet',
			'datas': data,
		}		


	@api.multi
	def print_payroll_sheet_5(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 5,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salarysheet',
			'datas': data,
		}		


	@api.multi
	def print_payroll_sheet_6(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 6,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salarysheet',
			'datas': data,
		}		

	@api.multi
	def print_payroll_accounts_1(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 1,
		}
		return self.env.ref('hr_payroll_ext.report_salary_accounts').report_action([], data=data, config=False)			
		
	@api.multi
	def print_payroll_accounts_3(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 3,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salaryaccounts',
			'datas': data,
		}
	
	@api.multi
	def print_payroll_accounts_4(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 4,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salaryaccounts',
			'datas': data,
		}		
		
	@api.multi
	def print_payroll_accounts_5(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 5,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salaryaccounts',
			'datas': data,
		}		
		
	@api.multi
	def print_payroll_accounts_6(self):						
		data = {
			'date_from': self.date_start[:10],
			'date_to': self.date_end[:10],
			'company_id': 6,
		}
		return {
			'type': 'ir.actions.report',
			'report_name': 'hr_payroll_ext.report_salaryaccounts',
			'datas': data,
		}
		
	def format_field_name(self, ordering, prefix='a', suffix='id'):
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)	

	def group_lines(self, line):
		line2 = {}
		for x, y, l in line:
			tmp = str(l['account_id'])
			if tmp in line2:
				am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
				line2[tmp]['debit'] = (am > 0) and am or 0.0
				line2[tmp]['credit'] = (am < 0) and -am or 0.0
			else:
				line2[tmp] = l

		line = []
		for key, val in line2.items():
			line.append((0, 0, val))
		return line

	@api.multi
	def transfer_salary_1(self,company_id,journal_id):
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']			
		slips_obj = self.env['hr.payslip']
		transfer_codes = self.env['hr.salary.transfer.codes']
		
		line_ids = []
		dr_line_ids = []
		
		slips = slips_obj.search([('company_id','=',company_id),('struct_id.company_id','!=',company_id),('date_from','>=',self.date_start),('date_to','<=',self.date_end),
			('state','=','done'),('transfered','!=',True)])
			
		if slips:
			name = _('Salary Transfer of Group Company Employees for %s') % ((datetime.strptime(self.date_end[:10],"%Y-%m-%d")).strftime('%B-%y'))
			move = {
				'narration': name,
				'ref': name,
				'journal_id': journal_id,
				'company_id': company_id,
				'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),
				'period_id': self.id,
			}
			for slip in slips:
		
				debit_account_id = transfer_codes.search([('company_id','=',company_id),('other_company_id','=',slip.struct_id.company_id.id),('account_type','=','current_account')]).account_id.id
				credit_account_id = transfer_codes.search([('company_id','=',company_id),('account_type','=','accrued_expense_salary')]).account_id.id
				other_account_id = transfer_codes.search([('company_id','=',slip.struct_id.company_id.id),('account_type','=','accrued_expense_salary')]).account_id.id

				line = move_line_obj.sudo().search([('move_id','=',slip.move_id.id),('account_id','=',other_account_id)])

				debit_line = (0, 0, {
					'name': 'Salary of ' + slip.struct_id.company_id.abbrev + ' Employees: Transfer by ' + slip.company_id.abbrev + '.' ,
					'company_id': company_id,
					'partner_id': False,
					'account_id': debit_account_id,
					'journal_id': journal_id,
					'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),			
					'debit': line.credit,
					'credit': line.debit,
					'analytic_account_id': False,
					'tax_line_id': False,
				})
				dr_line_ids.append(debit_line)

				credit_line = (0, 0, {
					'name': line.name,
					'company_id': company_id,
					'partner_id': False,
					'account_id': credit_account_id,
					'journal_id': journal_id,
					'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),					
					'debit': line.debit,
					'credit': line.credit,
					'analytic_account_id': False,
					'tax_line_id': False,
				})
				
				size = int(config.get_misc('analytic', 'analytic_size', 10))
				for n in range(1, size + 1):
					src = self.format_field_name(n,'a','id')
					dst = self.format_field_name(n,'a','id')
					credit_line[2].update({dst : line[src].id})
				
				credit_line[2].update({'d_bin' : line.d_bin})

				line_ids.append(credit_line)
			
			dr_line_ids = self.group_lines(dr_line_ids)
			line_ids += dr_line_ids
			
			move.update({'line_ids': line_ids})
			move = move_obj.sudo().create(move)

	@api.multi
	def transfer_salary_2(self,company_id,journal_id):
		move_obj = self.env['account.move']
		move_line_obj = self.env['account.move.line']			
		slips_obj = self.env['hr.payslip']
		transfer_codes = self.env['hr.salary.transfer.codes']

		line_ids = []
		cr_line_ids = []
		
		slips = slips_obj.search([('struct_id.company_id','=',company_id),('company_id','!=',company_id),('date_from','>=',self.date_start),('date_to','<=',self.date_end),
			('state','=','done')])   		

		if slips:
			name = _('Salary Transfer from Group Company Employees for %s') % ((datetime.strptime(self.date_end[:10],"%Y-%m-%d")).strftime('%B-%y'))
			move = {
				'narration': name,
				'ref': name,
				'journal_id': journal_id,
				'company_id': company_id,
				'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),			
				'period_id': self.id,
			}
			for slip in slips:
				
				debit_account_id = transfer_codes.search([('company_id','=',company_id),('account_type','=','accrued_expense_salary')]).account_id.id
				credit_account_id = transfer_codes.search([('company_id','=',company_id),('other_company_id','=',slip.company_id.id),('account_type','=','current_account')]).account_id.id
				other_account_id = transfer_codes.search([('company_id','=',slip.struct_id.company_id.id),('account_type','=','accrued_expense_salary')]).account_id.id

				line = move_line_obj.sudo().search([('move_id','=',slip.move_id.id),('account_id','=',other_account_id)])  # check

				debit_line = (0, 0, {
					'name': line.name,
					'company_id': company_id,
					'partner_id': False,
					'account_id': debit_account_id,
					'journal_id': journal_id,
					'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),			
					'debit': line.credit,
					'credit': line.debit,
					'analytic_account_id': False,
					'tax_line_id': False,
				})
				
				size = int(config.get_misc('analytic', 'analytic_size', 10))
				for n in range(1, size + 1):
					src = self.format_field_name(n,'a','id')
					dst = self.format_field_name(n,'a','id')
					debit_line[2].update({dst : line[src].id})
				
				debit_line[2].update({'d_bin' : line.d_bin})

				line_ids.append(debit_line)			

				credit_line = (0, 0, {
					'name': 'Salary of ' + slip.company_id.abbrev + ' Employees: Transfer by ' + slip.struct_id.company_id.abbrev + '.' ,
					'company_id': company_id,
					'partner_id': False,
					'account_id': credit_account_id,
					'journal_id': journal_id,
					'date': ((datetime.strptime(self.date_end[:10],"%Y-%m-%d"))+relativedelta(days=+3)).strftime('%Y-%m-%d'),			
					'debit': line.debit,
					'credit': line.credit,
					'analytic_account_id': False,
					'tax_line_id': False,
				})
				cr_line_ids.append(credit_line)				

			cr_line_ids = self.group_lines(cr_line_ids)
			line_ids += cr_line_ids
			
			
			move.update({'line_ids': line_ids})
			move = move_obj.sudo().create(move)

			slips.write({'transfered':True})
					
	
	@api.multi
	def get_midchem_working_days(self,payslip_id=None,code=None):
		worked_day_obj = self.env['hr.payslip.worked_days']
		worked_day_id = worked_day_obj.search([('payslip_id','=',payslip_id),('code','=',code)])
		return worked_day_id.number_of_days
	
	@api.multi	
	def get_midchem_lines(self,payslip_id,line_type=None,code=None):

		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
		amount =0
		if line_type == 'payslip_line':
			payslip_line_id = payslip_line_obj.search([('slip_id','=',payslip_id),('code','=',code)])
			amount = payslip_line_id.total or 0
		if line_type == 'input_line':
			input_id = payslip_input_obj.search([('payslip_id','=',payslip_id),('code','=',code)])
			amount=input_id.amount or 0
		return amount
	
	@api.multi
	def make_excel_1(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Salary Sheet")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
		worksheet.write_merge(0, 1, 0, 22,"Salary Sheet", style = style_title)
		
		row = 3
		col = 0
        		  
		table_header = ['EMP Code','Name','Position','Nationality','Salary Days','Basic','Earned','Housing','Arrears','Mobile Allowance','Food Allowance','Transport Allowance',
						'Petrol Allowance','OverTime Hours','OverTime','Incentives','Others','Gross','Advance','Loan','Other Deductions','GOSI Insurance','Net Salary']
		for i in range(23):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
		register_id = self.register_id.id
		run_ids = self.env['hr.payslip.run'].search([('register_id','=',register_id)])
		
		payslip_ids = self.env['hr.payslip'].search([('date_from','>=',self.date_start[:10]),('date_to','<=',self.date_end[:10]),('company_id','=',1),('payslip_run_id','in',run_ids.ids)],order='code')
	
		for payslip in payslip_ids:
			ot_hours = 0
			row += 1
			col = 0  
			worksheet.write(row,col, payslip.employee_id.code)
			col +=1
			worksheet.write(row,col, payslip.employee_id.name)
			col +=1
			worksheet.write(row,col, payslip.employee_id.job_id.name)
			col +=1
			worksheet.write(row,col, payslip.employee_id.country_id.name)
			col +=1
			worksheet.write(row,col, self.get_midchem_working_days(payslip.id,'WORK100'))
			col +=1
			worksheet.write(row,col, payslip.contract_id.wage)
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','BASIC'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','Accommodation'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','ARS'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','MA'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','FDA'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','TRA'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','FLA'))
			col +=1
			worksheet.write(row,col, ot_hours)
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','OT'))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','INCTV'))
			col +=1
			worksheet.write(row,col, abs(self.get_midchem_lines(payslip.id,'payslip_line','OA')))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','GROSS'))
			col +=1
			worksheet.write(row,col, abs(self.get_midchem_lines(payslip.id,'payslip_line','ADV')))
			col +=1
			worksheet.write(row,col, abs(self.get_midchem_lines(payslip.id,'payslip_line','LOAN')))
			col +=1
			worksheet.write(row,col, abs(self.get_midchem_lines(payslip.id,'payslip_line','ODE')))
			col +=1
			worksheet.write(row,col, abs(self.get_midchem_lines(payslip.id,'payslip_line','GSI')))
			col +=1
			worksheet.write(row,col, self.get_midchem_lines(payslip.id,'payslip_line','NET'))  
		        
		file_data = io.BytesIO()
		workbook.save(file_data)
		
		wiz_id = self.env['salary.sheet.save.wizard'].create({
			#'state': 'get',
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Salary Sheet.xls'
		})
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Salary Sheet Save Form',
			'res_model': 'salary.sheet.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': wiz_id.id,
			'target': 'new',
			'context': self._context,
		}
		
		
	
class hr_payperiod_schedule(models.Model):
	_name = 'hr.payroll.period.schedule'
	_description = "Payroll Period Schedule"

	def _tz_list(self):
		res = tuple()
		for name in common_timezones:
			res += ((name, name),)
		return res


	name = fields.Char('Description', size=256, required=True)
	tz = fields.Selection(_tz_list, 'Time Zone', required=True)
	paydate_biz_day = fields.Boolean('Pay Date on a Business Day')
	ot_week_startday = fields.Selection([
		('0', _('Sunday')),('1', _('Monday')),('2', _('Tuesday')),('3', _('Wednesday')),('4', _('Thursday')),('5', _('Friday')),('6', _('Saturday')),],
		'Start of Week', required=True,default='1')
	ot_max_rollover_hours = fields.Integer('OT Max. Continuous Hours', required=True,default='6')
	ot_max_rollover_gap = fields.Integer('OT Max. Continuous Hours Gap (in Min.)', required=True,default='60')
	type = fields.Selection([('manual', 'Manual'),('monthly', 'Monthly'),],'Type', required=True,default='monthly')
	mo_firstday = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),('8', '8'), ('9', '9'), ('10', '10'), 
		('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'),('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
		('21', '21'),('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),('29', '29'), ('30', '30'), ('31', '31'),],
		'Start Day',default='1')
	mo_paydate = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),('8', '8'), ('9', '9'), ('10', '10'), 
		('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'),('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
		('21', '21'),('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),('29', '29'), ('30', '30'), ('31', '31'),],
		'Pay Date',default='3')
	contract_ids = fields.One2many('hr.contract', 'pps_id', 'Contracts')
	pay_period_ids = fields.One2many('hr.payroll.period', 'schedule_id', 'Pay Periods')
	initial_period_date = fields.Date('Initial Period Start Date')
	active = fields.Boolean('Active',default=True)


	@api.multi
	def _check_initial_date(self):
		for obj in self:
			if obj.type in ['monthly'] and not obj.initial_period_date:
				return False
		return True

	_constraints = [(_check_initial_date,'You must supply an Initial Period Start Date', ['type']),]

	@api.multi
	def add_pay_period(self):

		def get_period_year(dt):
			month_number = 0
			year_number = 0
			if dt.day < 15:
				month_number = dt.month
				year_number = dt.year
			else:
				dtTmp = add_months(dt, 1)
				month_number = dtTmp.month
				year_number = dtTmp.year
			return month_number, year_number

		# XXX - Someone who cares about DST should update this code to handle it.
		schedule_obj = self.env['hr.payroll.period.schedule']

		data = None
		for sched in self:
			local_tz = timezone(sched.tz)
			try:
				latest = max(datetime.strptime(p.date_end, '%Y-%m-%d %H:%M:%S') for p in sched.pay_period_ids)
			except ValueError:
				latest = False

			if not latest:
				# No pay periods have been defined yet for this pay period schedule.
				if sched.type == 'monthly':
					dtStart = datetime.strptime(sched.initial_period_date, '%Y-%m-%d')
					if dtStart.day > int(sched.mo_firstday):
						dtStart = add_months(dtStart, 1)
						dtStart = datetime(dtStart.year, dtStart.month, int(sched.mo_firstday), 0, 0, 0)
					elif dtStart.day < int(sched.mo_firstday):
						dtStart = datetime(dtStart.year, dtStart.month, int(sched.mo_firstday), 0, 0, 0)
					else:
						dtStart = datetime(dtStart.year, dtStart.month, dtStart.day, 0, 0, 0)
					dtEnd = add_months(dtStart, 1) - timedelta(days=1)
					dtEnd = datetime(dtEnd.year, dtEnd.month, dtEnd.day, 23, 59, 59)
					month_number, year_number = get_period_year(dtStart)

					# Convert from time zone of punches to UTC for storage
					utcStart = local_tz.localize(dtStart, is_dst=None)
					utcStart = utcStart.astimezone(utc)
					utcEnd = local_tz.localize(dtEnd, is_dst=None)
					utcEnd = utcEnd.astimezone(utc)
					
					data = {
						'name': 'Pay Period ' + str(month_number) + '/' + str(year_number),
						'schedule_id': sched.id,
						'date_start': utcStart.strftime('%Y-%m-%d %H:%M:%S'),
						'date_end': utcEnd.strftime('%Y-%m-%d %H:%M:%S'),
					}
			else:
				if sched.type == 'monthly':
					# Convert from UTC to timezone of punches
					utcStart = latest #datetime.strptime(latest, '%Y-%m-%d %H:%M:%S')
					utc_tz = timezone('UTC')
					utcStart = utc_tz.localize(utcStart, is_dst=None)
					utcStart += timedelta(seconds=1)
					dtStart = utcStart.astimezone(local_tz)
					
					# Roll forward to the next pay period start and end times
					dtEnd = add_months(dtStart, 1) - timedelta(days=1)
					dtEnd = datetime(dtEnd.year, dtEnd.month, dtEnd.day, 23, 59, 59)
					month_number, year_number = get_period_year(dtStart)

					# Convert from time zone of punches to UTC for storage
					utcStart = dtStart.astimezone(utc_tz)
					utcEnd = local_tz.localize(dtEnd, is_dst=None)
					utcEnd = utcEnd.astimezone(utc)
					
					data = {
						'name': 'Pay Period ' + str(month_number) + '/' + str(year_number),
						'schedule_id': sched.id,
						'date_start': utcStart.strftime('%Y-%m-%d %H:%M:%S'),
						'date_end': utcEnd.strftime('%Y-%m-%d %H:%M:%S'),
					}
			if data is not None:
				sched.write({'pay_period_ids': [(0, 0, data)]})

	@api.one
	def _get_latest_period(self):
		try:
			latest_period = max(datetime.strptime(period.date_end, '%Y-%m-%d %H:%M:%S') for period in self.pay_period_ids)
		except ValueError:
			latest_period = False
		return latest_period

	def try_create_new_period(self):
		"""Try and create pay periods for up to 3 months from now."""
		# TODO - Someone who cares about DST should update this code to handle it.

		dtNow = datetime.now()
		utc_tz = timezone('UTC')
		sched_obj = self.env['hr.payroll.period.schedule']
		sched_ids = sched_obj.search([])
		for sched in sched_ids:
			if sched.type == 'monthly':
				firstday = sched.mo_firstday
			else:
				continue
			dtNow = datetime.strptime(dtNow.strftime('%Y-%m-' + firstday + ' 00:00:00'), '%Y-%m-%d %H:%M:%S')
			loclDTNow = timezone(sched.tz).localize(dtNow, is_dst=False)
			utcDTFuture = loclDTNow.astimezone(utc_tz) + relativedelta(months=+3)

			if not sched.pay_period_ids:
				sched.add_pay_period()

			latest_period = sched._get_latest_period()
			utcDTStart = utc_tz.localize(datetime.strptime(latest_period.date_start, '%Y-%m-%d %H:%M:%S'), is_dst=False)
			while utcDTFuture > utcDTStart:
				sched.add_pay_period()
				latest_period = sched._get_latest_period()
				utcDTStart = utc_tz.localize(datetime.strptime(latest_period.date_start, '%Y-%m-%d %H:%M:%S'),is_dst=False)


class contract_template(models.Model):
	_inherit = 'hr.contract.template'

	pay_sched_id = fields.Many2one('hr.payroll.period.schedule', 'Payroll Period Schedule',readonly=True, states={'draft': [('readonly', False)]})


class hr_contract(models.Model):
	_inherit = 'hr.contract'

	def _get_pay_sched(self):
		template = self.get_latest_template()
		return template and template.pay_sched_id or self.env['hr.payroll.period.schedule']

	pps_id = fields.Many2one('hr.payroll.period.schedule', 'Payroll Period Schedule',default=_get_pay_sched)


class hr_payslip_amendment(models.Model):
	_inherit = 'hr.payslip.amendment'

	pay_period_id = fields.Many2one('hr.payroll.period', 'Pay Period',domain=[('state', 'in', ['open', 'ended', 'locked', 'generate'])],required=False,readonly=True,
			states={
				'draft': [('readonly', False)],
				'validate': [('required', True)],
				'done': [('required', True)]
			},)



class hr_holidays_status(models.Model):
	_inherit = 'hr.leave.type'

	code = fields.Char('Code', size=16,)
	
	_sql_constraints = [('code_unique', 'UNIQUE(code)','Codes for leave types must be unique!')]


class hr_holidays(models.Model):
	_inherit = 'hr.leave'

	payroll_period_state = fields.Selection([('unlocked', 'Unlocked'), ('locked', 'Locked')],'Payroll Period State', readonly=True,default='unlocked')

	@api.multi
	def unlink(self):
		for h in self:
			if h.payroll_period_state == 'locked':
				raise UserError(_('Warning!\nYou cannot delete a leave which belongs to a payroll period that has been locked.'))
		return super(hr_holidays, self).unlink()
			
		
class hr_employee_month_attendance_variations(models.Model):
	_name = "hr.employee.month.attendance.variations"
	_description = "Month Attendance Variations"
	_inherit = ['mail.thread']
	_order = 'id desc'
	
	period_id = fields.Many2one('hr.payroll.period','Payroll Period', order='id desc')
	from_date = fields.Datetime('From Date', related='period_id.date_start')
	to_date = fields.Datetime('To Date', related='period_id.date_end')
	
	employee_id = fields.Many2one('hr.employee', "Employee",track_visibility='always',required=True,readonly=True,states={'draft': [('readonly', False)]})
	days = fields.Integer('Days',required=True,readonly=True,states={'draft': [('readonly', False)]})
	note = fields.Text('Description',readonly=True,states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',track_visibility='onchange',default='draft')
	contract_id = fields.Many2one('hr.contract', "Contract")
	
	@api.multi
	def name_get(self):
		result = []
		for rec in self:
			result.append((rec.id, _("%(empl_code)s - %(period)s") % {
				'empl_code': rec.employee_id.code,
				'period': rec.period_id.name,
			}))
		return result
			
	@api.multi
	def variation_confirm(self):
		self.state = 'done'


class salary_sheet_save_wizard(models.TransientModel):
    _name = "salary.sheet.save.wizard"
    _description = 'Salary Sheet Save Wizard'
    
    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)		
		
