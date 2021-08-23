import pdb
import babel
import calendar
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import common_timezones, timezone, utc
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT

from odoo.tools import float_compare, float_is_zero
import math

import logging
_logger = logging.getLogger(__name__)


def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()


def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')


def dateToStr(ddate):
	return ddate.strftime('%Y-%m-%d')


def datetimeToStr(ddate):
	return ddate.strftime('%Y-%m-%d %H:%M:%S')


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


def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year, month)[1])
	return datetime(year, month, day)


class hr_payslip(models.Model):
	_name = 'hr.payslip'
	_inherit = ['hr.payslip','mail.thread', 'mail.activity.mixin', 'portal.mixin']

	@api.model
	def _default_journal(self):
		company_id = self._context.get('company_id', self.env.user.company_id.id)
		domain = [
			('code', '=', 'SAL'),
			('company_id', '=', company_id),
		]
		return self.env['account.journal'].search(domain, limit=1)
		
	@api.multi
	@api.depends('line_ids','line_ids.total')	
	def _calculate_total(self):
		for rec in self:
			total = 0
			line_ids = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id), ('code', '=', 'NET')])
			for line in line_ids:
				if line.total:
					total += line.total
				else:
					total += float(line.quantity) * line.amount
			rec.total = total

	exception_ids = fields.One2many('hr.payslip.exception', 'slip_id','Exceptions', readonly=True)
	advice_id = fields.Many2one('hr.payroll.advice', 'Bank Advice', copy=False)
	journal_id = fields.Many2one('account.journal', 'Salary Journal',states={'draft': [('readonly', False)]}, readonly=True, required=True,default=_default_journal)
	date_from = fields.Date('Date From', readonly=True, states={'draft': [('readonly', False)]}, required=True, default = lambda *a: str(datetime.now()+ relativedelta.relativedelta(months=-1) + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', readonly=True, states={'draft': [('readonly', False)]}, required=True, default= lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10],)
	code = fields.Char('Code',related='employee_id.code',store=True)
	payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches',readonly=False, copy=False)
	send_sms = fields.Boolean('SMS Sent', defult=False)
	send_email = fields.Boolean('Email Sent', default=False)
	total = fields.Float(compute='_calculate_total', string='Net', track_visibility='onchange')
	bank_id = fields.Many2one('sos.bank','Bank Name')
	bankacctitle = fields.Char('Account Title')
	bankacc = fields.Char('Account No')
	staff_attendance_line_ids = fields.One2many('sos.guard.attendance1', 'staff_slip_id', 'Attendance Days')
	
	def get_line_salary(self,code=None):
		total = 0
		if code == 'ADV':
			lines = self.env['hr.payslip.line'].search([('slip_id','=',self.id),('code','in',('LOAN','ADV'))])
		else:
			lines = self.env['hr.payslip.line'].search([('slip_id','=',self.id),('code','=',code)])
		for line in lines:
			total += abs(line.total)
		return total

	@api.model
	def create(self, vals):
		slip_id = super(hr_payslip, self).create(vals)
		slip_id.bank_id =  slip_id.employee_id.bank_id and slip_id.employee_id.bank_id.id or False
		slip_id.bankacctitle =  slip_id.employee_id.bankacctitle and slip_id.employee_id.bankacctitle or ''
		slip_id.bankacc =  slip_id.employee_id.bankacc and slip_id.employee_id.bankacc or ''
		att_recs = self.get_attendance_lines(slip_id.employee_id, slip_id.date_from, slip_id.date_to)
		att_recs.write({'staff_slip_id': slip_id.id})
		return slip_id

	@api.multi
	def unlink(self):
		for payslip in self:
			if payslip.state not in ['draft', 'cancel']:
				raise Warning(_('You cannot delete a payslip which is not draft or cancelled!'))
			att_ids = self.env['sos.guard.attendance1'].search([('employee_id','=',payslip.employee_id.id),('staff_slip_id','=',payslip.id)])
			att_ids.write({'staff_slip_id':False})
		return super(hr_payslip, self).unlink()

	
	@api.multi
	def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
		#defaults
		res = {
			'value': {
				'line_ids': [],
				#delete old input lines
				'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
				#delete old worked days lines
				'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
				#'details_by_salary_head':[], TODO put me back
				'name': '',
				'contract_id': False,
				'struct_id': False,
			}
		}
		if (not employee_id) or (not date_from) or (not date_to):
			return res

		ttyme = date_from
		employee = self.env['hr.employee'].browse(employee_id)
		locale = self.env.context.get('lang') or 'en_US'
		res['value'].update({
			'name': _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
			'company_id': employee.company_id.id,
			'bank_id' : employee.bank_id and employee.bank_id.id or False,
			'bankacctitle' : employee.bankacctitle and employee.bankacctitle or '',
			'bankacc' : employee.bankacc and employee.bankacc or '',
		})
		if not contract_id and not self.env.context.get('contract'):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(employee, date_from, date_to)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(employee, date_from, date_to)

		if not contract_ids:
			return res
		contract = self.env['hr.contract'].browse(contract_ids[0])
		res['value'].update({
			'contract_id': contract.id
		})
		struct = contract.struct_id
		if not struct:
			return res
		res['value'].update({
			'struct_id': struct.id,
		})

		#computation of the salary input
		contracts = self.env['hr.contract'].browse(contract_ids)
		worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
		input_line_ids = self.get_inputs(contracts, date_from, date_to)
		staff_attendance_line_ids = self.get_attendance_lines(employee, date_from,date_to)
		res['value'].update({
			'worked_days_line_ids': worked_days_line_ids,
			'input_line_ids': input_line_ids,
			'staff_attendance_line_ids': staff_attendance_line_ids,
		})
		return res

	@api.onchange('employee_id', 'date_from','date_to','contract_id')
	def onchange_employee_or_date(self):
		if (not self.employee_id) or (not self.date_from) or (not self.date_to):
			return
		employee_id = self.employee_id
		date_from = self.date_from
		date_to = self.date_to
		contract_id = self.contract_id or False

		self.name = _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(date_to.strftime('%B-%Y')))
		self.company_id = employee_id.company_id
		self.bank_id = employee_id.bank_id and employee_id.bank_id.id or False
		self.bankacctitle = employee_id.bankacctitle and employee_id.bankacctitle or ''
		self.bankacc = employee_id.bankacc and employee_id.bankacc or ''

		contract_ids = self.env['hr.contract']
		cont_ids = [0]
		
		if contract_id: 
			self.contract_id = contract_id or False 
			cont_ids = contract_id.id
			cont_ids = [cont_ids]
			
		if not contract_id and not self.contract_id:
			if not self.env.context.get('contract') or not self.contract_id:
				cont_ids = self.get_contract(employee_id, date_from, date_to)
				if not cont_ids:
					return
				self.contract_id = self.contract_id.browse(cont_ids[0])
		if not self.contract_id.struct_id:
			return

		self.struct_id = self.contract_id.struct_id
		if self.contract_id.journal_id:
			self.journal_id = self.contract_id.journal_id

		#computation of the salary input
		contract_ids = self.env['hr.contract'].search([('id','in',cont_ids)])
		worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
		worked_days_lines = self.worked_days_line_ids.browse([])
		
		if worked_days_line_ids:
			for r in worked_days_line_ids:
				worked_days_lines += worked_days_lines.new(r)
			self.worked_days_line_ids = worked_days_lines
			
		input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
		input_lines = self.input_line_ids.browse([])
		if input_line_ids:
			for r in input_line_ids:
				input_lines += input_lines.new(r)
			self.input_line_ids = input_lines
		self.get_attendance_lines2(self.employee_id, self.date_from, self.date_to)
		return

	@api.multi
	def get_attendance_lines(self, employee, date_from, date_to):
		att_line_pool = self.env['sos.guard.attendance1']
		if not employee:
			return False
		att_ids = att_line_pool.search(
			[('name', '>=', date_from), ('name', '<=', date_to), ('employee_id', '=', employee.id), '|',
			 ('slip_id', '=', False), ('slip_id', 'in', self.ids)])
		return att_ids

	@api.multi
	def get_attendance_lines2(self, employee, date_from, date_to):
		for slip in self:
			att_line_pool = self.env['sos.guard.attendance1']
			if not employee:
				return False
			att_ids = att_line_pool.search(
				[('employee_id', '=', employee.id), ('staff_slip_id', '=', slip.id)])
			att_ids.write({'staff_slip_id': False})
			att_ids = att_line_pool.search([
				('name', '>=', date_from), ('name', '<=', date_to),('employee_id', '=', employee.id),
				'|', ('staff_slip_id', '=', False),('staff_slip_id', '=', slip.id)
			])
			att_ids.write({'staff_slip_id': slip.id})



	@api.multi
	def process_sheet(self):
		move_pool = self.env['account.move']
		precision = self.env['decimal.precision'].precision_get('Payroll')
		model_rec = self.env['ir.model'].search([('model','=','hr.payslip.line')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')

		for slip in self:
			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			date = slip.date_to
			company_id = slip.company_id.id

			name = (_('Being Charge of Salary %s') % (slip.number))
			move = {
				'narration': name,
				'ref': slip.number,
				'journal_id': slip.journal_id.id,
				'company_id': company_id,
				'date': date,
			}
			for line in slip.details_by_salary_rule_category:
				#amt = slip.credit_note and -line.total or line.total
				amt = abs(slip.credit_note and -line.total or line.total)
				if float_is_zero(amt, precision_digits=precision):
					continue
				debit_account_id = line.salary_rule_id.account_debit.id
				credit_account_id = line.salary_rule_id.account_credit.id

				#if flag:
				if debit_account_id:
					debit_line = (0, 0, {
						'name': _('Charging of Salary %s') % (slip.number),
						'company_id': company_id,
						'partner_id': line._get_partner_id(credit_account=False),
						'account_id': debit_account_id,
						'journal_id': slip.journal_id.id,
						'date': date,
						'debit': amt > 0.0 and amt or 0.0,
						'credit': amt < 0.0 and -amt or 0.0,
						'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
						'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
					})
					line_ids.append(debit_line)
					debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

				if credit_account_id:
					credit_line = (0, 0, {
						'name': _('%s %s') % (line.name,slip.number),
						'company_id': company_id,
						'partner_id':line._get_partner_id(credit_account=True),
						'account_id': credit_account_id,
						'journal_id': slip.journal_id.id,
						'date': date,
						'debit': amt < 0.0 and -amt or 0.0,
						'credit': amt > 0.0 and amt or 0.0,
						'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
						'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
					})
					line_ids.append(credit_line)
					credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
					
			for move_line in line_ids:
				number = 0
				nd_ids = eval("self.env['account.account'].browse(move_line[2].get('account_id')).nd_ids")
				if nd_ids:
					for auto_entry in auto_entries:
						if auto_entry.dimension_id in nd_ids:
							if auto_entry.src_fnc:
								move_line[2].update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
							else:
								move_line[2].update({auto_entry.dst_col.name : eval('self.'+auto_entry.src_col.name).id})

							ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])
							number += math.pow(2,int(ans.ordering)-1)
					move_line[2].update({'d_bin' : bin(int(number))[2:].zfill(10)})

			move.update({'line_ids': line_ids})
			move_id = move_pool.create(move)
			#move_id.action_post() need to check
			slip.staff_attendance_line_ids.write({'state': 'done'})
			slip.write({'move_id': move_id.id, 'date' : date,'state': 'done'})
			
	@api.multi
	def send_payslip_email(self):
		for rec in self:
			template = self.env.ref('hr_payroll_ext.payslip_email_template')	
			rec.message_post_with_template(template.id, composition_mode='comment')
			rec.send_email = True

	def _partial_period_factor(self, payslip, contract):
		dpsFrom = payslip.date_from
		dpsTo = payslip.date_to
		dcStart = contract.date_start
		dcEnd = False
		if contract.date_end:
			dcEnd = contract.date_end

		# both start and end of contract are out of the bounds of the payslip
		if dcStart <= dpsFrom and (not dcEnd or dcEnd >= dpsTo):
			return 1

		# One or both start and end of contract are within the bounds of the payslip
		no_contract_days = 0
		if dcStart > dpsFrom:
			no_contract_days += (dcStart - dpsFrom).days
		if dcEnd and dcEnd < dpsTo:
			no_contract_days += (dpsTo - dcEnd).days

		total_days = (dpsTo - dpsFrom).days + 1
		contract_days = total_days - no_contract_days
		return float(contract_days) / float(total_days)

	def get_utilities_dict(self, contract, payslip):
		res = {}
		if not contract or not payslip:
			return res
		# Calculate percentage of pay period in which contract lies
		res['PPF'] = {
			'amount': self._partial_period_factor(payslip, contract),
		}

		# Calculate net amount of previous payslip
		ps_ids = self.env['hr.payslip'].search([('employee_id', '=', contract.employee_id.id)], order='date_from')
		res.update({
			'PREVPS': {
				'exists': 0,
				'net': 0
			}
		})
		if ps_ids:
			# Get database ID of Net salary category
			res_model, net_id = self.env['ir.model.data'].get_object_reference('hr_payroll', 'NET')
			res['PREVPS']['exists'] = 1
			total = 0
			for line in ps_ids[-1].line_ids:
				if line.salary_rule_id.category_id.id == net_id:
					total += line.total
			res['PREVPS']['net'] = total
		return res

	# YTI TODO contract_ids should be a browse record
	@api.model
	def get_inputs(self, contracts, date_from, date_to):
		res = []
		contract_obj = self.env['hr.contract']
		rule_obj = self.env['hr.salary.rule']
		arrears_obj = self.env['hr.salary.inputs']
		structure_ids = contracts.get_all_structures()
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
		for contract in contracts:
			for rule in rule_obj.browse(sorted_rule_ids):
				if rule.input_ids:
					for input in rule.input_ids:
						arr_amt = ''
						arr_ids = arrears_obj.search([('employee_id', '=', contract.employee_id.id), ('name', '=', input.code),('date', '>=', date_from), ('date', '<=', date_to), ('state', '=', 'confirm')])
						if arr_ids:
							arr_amt = 0
							for arr_id in arr_ids:
								arr_amt += arr_id.amount
						inputs = {
							'name': input.name,
							'code': input.code,
							'contract_id': contract.id,
							'amount': arr_amt or 0,
						}
						res += [inputs]
		return res

	@api.multi
	def compute_sheet(self):
		for payslip in self:
			# Changed the Number Style
			ttyme = payslip.date_from
			number = _('Slip-%s-%s') % (tools.ustr(ttyme.strftime('%y%m')), payslip.employee_id.code)
			# delete old payslip lines
			payslip.line_ids.unlink()

			# set the list of contract for which the rules have to be applied
			# if we don't give the contract, then the rules to apply should be for all current contracts of the employee
			contract_ids = payslip.contract_id.ids or self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)

			arr_ids = self.env['hr.salary.inputs'].search([('employee_id', '=', payslip.employee_id.id),('date', '>=', payslip.date_from),('date', '<=', payslip.date_to), ('state', '=', 'confirm')])
			if arr_ids:
				ot_inputs = arr_ids.filtered(lambda z: z.name == 'OT')
				if ot_inputs:
					for ot_input in ot_inputs:
						if ot_input.ot_id:
							ot_input.ot_id.overtime_status = 'post'
				loan_inputs = arr_ids.filtered(lambda z: z.name == 'LOAN')
				if loan_inputs:
					for loan_input in loan_inputs:
						if loan_input.name == 'LOAN' and loan_input.loan_line:
							loan_input.loan_line.paid = True
				arr_ids.write({'state': 'done', 'slip_id': payslip.id})

			payslip.staff_attendance_line_ids.write({'state': 'counted'})
			month_att_ids = self.env['hr.employee.month.attendance'].search([('employee_id', '=', payslip.employee_id.id),('date', '>=', payslip.date_from),('date', '<=', payslip.date_to)])
			if month_att_ids:
				month_att_ids.write({'state': 'done', 'slip_id': payslip.id})

			lines = [(0, 0, line) for line in self.get_payslip_lines(contract_ids, payslip.id)]
			payslip.write({'line_ids': lines, 'number': number})

			#For SMS
			if not payslip.send_sms:
				slip_month = (tools.ustr(ttyme.strftime('%B-%Y')))
				text = "Dear Mr./Ms. " + payslip.employee_id.name + ", \n Your Salary For the Month of " + slip_month + " has been Generated. \n Regards, SOS."
				message = self.env['send_sms'].render_template(text, 'hr.payslip', payslip.id)
				mobile_no = (payslip.employee_id.mobile_phone and payslip.employee_id.mobile_phone) or (
							payslip.employee_id.work_phone and payslip.employee_id.work_phone) or False
				gatewayurl_id = self.env['gateway_setup'].search([('id', '=', 1)])
				if mobile_no:
					self.env['send_sms'].send_sms_link(message, mobile_no, payslip.id, 'hr.payslip', gatewayurl_id)
		return True

	@api.model
	def get_payslip_lines(self, contract_ids, payslip_id):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			if category.code in localdict['categories'].dict:
				localdict['categories'].dict[category.code] = localdict['categories'].dict[category.code] + amount
			else:
				localdict['categories'].dict[category.code] = amount
			return localdict

		class BrowsableObject(object):

			def __init__(self, employee_id, dict, env):
				self.employee_id = employee_id
				self.dict = dict
				self.env = env

			def __getattr__(self, attr):
				return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
						SELECT sum(amount) as sum
						FROM hr_payslip as hp, hr_payslip_input as pi 
						WHERE hp.employee_id = %s AND hp.state = 'done' 
						AND hp.date_from >= %s AND hp.date_to <= %s 
						AND hp.id = pi.payslip_id AND pi.code = %s""",
									(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()[0] or 0.0

		class LoanLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
						SELECT sum(amount) as sum 
						FROM hr_payslip as hp, hr_payslip_loan as pl 
						WHERE hp.employee_id = %s AND hp.state = 'done' 
						AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.payslip_id AND pl.code = %s""",
									(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()[0] or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
						SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours 
						FROM hr_payslip as hp, hr_payslip_worked_days as pi 
						WHERE hp.employee_id = %s AND hp.state = 'done' 
						AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
									(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()

			def sum(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[0] or 0.0

			def sum_hours(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[1] or 0.0

		class Payslips(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
						SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end) 
						FROM hr_payslip as hp, hr_payslip_line as pl 
						WHERE hp.employee_id = %s AND hp.state = 'done' 
						AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
									(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()
				return res and res[0] or 0.0

		# we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules_dict = {}
		worked_days_dict = {}
		categories_dict = {}
		inputs_dict = {}
		loans_dict = {}
		blacklist = []

		payslip = self.env['hr.payslip'].browse(payslip_id)

		for worked_days_line in payslip.worked_days_line_ids:
			worked_days_dict[worked_days_line.code] = worked_days_line

		for input_line in payslip.input_line_ids:
			inputs_dict[input_line.code] = input_line

		for loan_line in payslip.employee_id.loan_ids:
			loans_dict[loan_line.code] = loan_line

		categories = BrowsableObject(payslip.employee_id.id, categories_dict, self.env)
		inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
		loans = LoanLine(payslip.employee_id.id, loans_dict, self.env)
		worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
		payslips = Payslips(payslip.employee_id.id, payslip, self.env)
		rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

		baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
						 'inputs': inputs, 'loans': loans}
		# get the ids of the structures on the contracts and their parent id as well
		contracts = self.env['hr.contract'].browse(contract_ids)
		structure_ids = contracts.get_all_structures()
		# get the rules of the structure and thier children
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		# run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
		sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

		for contract in contracts:
			employee = contract.employee_id

			## These lines (before for) )are added for utils object , Plus utils is added in localdict
			temp_dict = {}
			utils_dict = self.get_utilities_dict(contract, payslip)
			for k, v in utils_dict.items():
				k_obj = BrowsableObject(payslip.employee_id.id, v, self.env)
				temp_dict.update({k: k_obj})
			utils = BrowsableObject(payslip.employee_id.id, temp_dict, self.env)

			localdict = dict(baselocaldict, employee=employee, contract=contract, utils=utils)

			for rule in sorted_rules:
				key = rule.code + '-' + str(contract.id)
				localdict['result'] = None
				localdict['result_qty'] = 1.0
				localdict['result_rate'] = 100
				# check if the rule can be applied
				if rule._satisfy_condition(localdict) and rule.id not in blacklist:
					# compute the amount of the rule
					amount, qty, rate = rule._compute_rule(localdict)
					# check if there is already a rule computed with that code
					previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
					# set/overwrite the amount computed for this rule in the localdict
					tot_rule = amount * qty * rate / 100.0
					localdict[rule.code] = tot_rule
					rules_dict[rule.code] = rule
					# sum the amount for its salary category
					localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
					# create/overwrite the rule in the temporary results
					result_dict[key] = {
						'salary_rule_id': rule.id,
						'contract_id': contract.id,
						'name': rule.name,
						'code': rule.code,
						'category_id': rule.category_id.id,
						'sequence': rule.sequence,
						'appears_on_payslip': rule.appears_on_payslip,
						'condition_select': rule.condition_select,
						'condition_python': rule.condition_python,
						'condition_range': rule.condition_range,
						'condition_range_min': rule.condition_range_min,
						'condition_range_max': rule.condition_range_max,
						'amount_select': rule.amount_select,
						'amount_fix': rule.amount_fix,
						'amount_python_compute': rule.amount_python_compute,
						'amount_percentage': rule.amount_percentage,
						'amount_percentage_base': rule.amount_percentage_base,
						'register_id': rule.register_id.id,
						'amount': amount,
						'employee_id': contract.employee_id.id,
						'quantity': qty,
						'rate': rate,
					}
				else:
					# blacklist this rule and its children
					blacklist += [id for id, seq in rule._recursive_search_of_rules()]

			## For Exception Checking
			localdict.update({'result': None})
			rule_ids = self.env['hr.payslip.exception.rule'].search([('active', '=', True)], order='sequence')

			for rule in rule_ids:
				if rule.satisfy_condition(localdict):
					val = {
						'name': rule.name,
						'slip_id': payslip.id,
						'rule_id': rule.id,
					}
					self.env['hr.payslip.exception'].create(val)
			## End Exception Checking

			result = [value for code, value in result_dict.items()]
			return result

	@api.model
	def get_worked_day_lines(self, contract_ids, date_from, date_to):
		for contract in contract_ids:
			attendance_policy = contract.employee_id.company_id.attendance_policy
			attendance_policy = 'daily' #SARFRAZ
			if not attendance_policy:
				attendance_policy = contract.company_id.attendance_policy
			if not attendance_policy:
				attendance_policy = self.env['res.company'].search([('id', '=', 1)]).attendance_policy

			if attendance_policy == 'none':
				return super(hr_payslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
			elif attendance_policy == 'daily':
				return self.get_worked_day_lines_attendance(contract_ids, date_from, date_to)
			elif attendance_policy in ('bio_month', 'monthly'):
				return self.get_worked_day_lines_monthly_attendance(contract_ids, date_from, date_to)

	def get_worked_day_lines_monthly_attendance(self, contract_ids, date_from, date_to):
		res = []
		for contract in contract_ids:
			attendances = {
				'MAX': {
					'name': _("Maximum Possible Working Hours"),
					'sequence': 1,
					'code': 'MAX',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				},
				'WORK100': {
					'name': _("Normal Working Days paid at 100%"),
					'sequence': 2,
					'code': 'WORK100',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				},
			}

			leaves = {}
			day_from = date_from
			day_to = date_to

			attendance_ids = self.env['hr.employee.month.attendance'].search(
				[('employee_id', '=', contract.employee_id.id), ('date', '>=', date_from), ('date', '<=', date_to)])
			# ('date','>=',date_from),('date','<=',date_to),('slip_id','=',False)])

			if len(attendance_ids) > 1:
				attendance_ids = attendance_ids.filtered(lambda att: att.contract_id.id == contract.id)

			if attendance_ids:
				for attendance in attendance_ids:
					attendances['WORK100']['number_of_days'] += attendance.present_days
					attendances['WORK100']['number_of_hours'] += attendance.present_days * 8

					attendances['MAX']['number_of_days'] += attendance.total_days
					attendances['MAX']['number_of_hours'] += attendance.total_days * 8

				leaves = []
				attendances = [value for key, value in attendances.items()]

				res += attendances + leaves
		return res

	def get_worked_day_lines_attendance(self, contract_ids, date_from, date_to):
		def was_on_leave(employee_id, datetime_day):
			day = datetime_day.strftime("%Y-%m-%d")
			holiday_ids = self.env['hr.leave'].search(
				[('state', '=', 'validate'), ('employee_id', '=', employee_id),
				 ('date_from', '<=', day), ('date_to', '>=', day)])
			return holiday_ids and holiday_ids[0].holiday_status_id.name or False

		res = []
		for contract in contract_ids:
			if not contract.resource_calendar_id:
				# fill only if the contract as a working schedule linked
				continue
			attendances = {
				'MAX': {
					'name': _("Maximum Possible Working Hours"),
					'sequence': 1,
					'code': 'MAX',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				},
				'WORK100': {
					'name': _("Normal Working Days paid at 100%"),
					'sequence': 2,
					'code': 'WORK100',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				},
				'HDAYS100': {
					'name': _("Public Holidays paid at 100%"),
					'sequence': 3,
					'code': 'HDAYS100',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				},
			}

			leaves = {}
			day_from = date_from
			day_to = date_to
			nb_of_days = (day_to - day_from).days + 1

			#Employee is AEX from Attendance
			if 'AEX' in contract.employee_id.category_ids.mapped('name'):
				attendances['MAX']['number_of_days'] = nb_of_days
				attendances['MAX']['number_of_hours'] = nb_of_days * 8
				attendances['WORK100']['number_of_days'] = nb_of_days
				attendances['WORK100']['number_of_hours'] = nb_of_days * 8

			else:
				#if Attendance Records found for this employee
				emp_atts = self.env['sos.guard.attendance1'].search(
								[('employee_id', '=', contract.employee_id.id),
								 ('name', '>=', date_from),
								 ('name','<=',date_to),
								 ('action','!=','out')])
				if emp_atts:
					for day in range(0, nb_of_days):
						#working_hours_on_day = self.env['resource.calendar'].working_hours_on_day(contract.working_hours, day_from + timedelta(days=day))
						working_hours_on_day = 8
						if working_hours_on_day:
							#the employee had to work
							leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day))
							if leave_type:
								# if he was on leave, fill the leaves dict
								if leave_type in leaves:
									leaves[leave_type]['number_of_days'] += 1.0
									leaves[leave_type]['number_of_hours'] += working_hours_on_day
								else:
									leaves[leave_type] = {
										'name': leave_type,
										'sequence': 5,
										'code': leave_type,
										'number_of_days': 1.0,
										'number_of_hours': working_hours_on_day,
										'contract_id': contract.id,
									}
							# attendances['WORK100']['number_of_days'] += 1.0
							# attendances['WORK100']['number_of_hours'] += working_hours_on_day
							else:
								attendance_id = self.env['sos.guard.attendance1'].search(
									[('employee_id', '=', contract.employee_id.id),
									 ('name', '>=', day_from + timedelta(days=day)),
									 ('name','<=',day_from + timedelta(days=day)),
									 ('action','!=','out')])

								if attendance_id:
									attendance_id = attendance_id[0]
									attendances['WORK100']['number_of_days'] += 1.0
									attendances['WORK100']['number_of_hours'] += working_hours_on_day
								if not attendance_id:
									pub_holiday = self.env['hr.holidays.public.line'].search([('date', '>=', day_from + timedelta(days=day)),('date','<=',day_from + timedelta(days=day))])
									if pub_holiday and not contract.employee_id.resigdate and contract.employee_id.appointmentdate <= pub_holiday.date:
										# attendances['WORK100']['number_of_days'] += 1.0
										# attendances['WORK100']['number_of_hours'] += working_hours_on_day
										attendances['HDAYS100']['number_of_days'] += 1.0
										attendances['HDAYS100']['number_of_hours'] += working_hours_on_day
									if pub_holiday and contract.employee_id.resigdate and contract.employee_id.resigdate >= pub_holiday.date :
											attendances['HDAYS100']['number_of_days'] += 1.0
											attendances['HDAYS100']['number_of_hours'] += working_hours_on_day

							attendances['MAX']['number_of_days'] += 1.0
							attendances['MAX']['number_of_hours'] += working_hours_on_day

			leaves = [value for key, value in leaves.items()]
			attendances = [value for key, value in attendances.items()]

			res += attendances + leaves
		return res

	def holidays_list_init(self, dFrom, dTo):
		holiday_obj = self.env['hr.holidays.public']
		res = holiday_obj.get_holidays_list(dFrom.year)
		if dTo.year != dFrom.year:
			res += holiday_obj.get_holidays_list(dTo.year)
		return res

	def leaves_list_init(self, employee_id, dFrom, dTo, tz):
		"""Returns a list of tuples containing start, end dates for leaves within the specified period.
        """

		leave_obj = self.env['hr.holidays']
		dtS = datetime.strptime(dFrom.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
		dtE = datetime.strptime(dTo.strftime(OE_DATEFORMAT) + ' 23:59:59', OE_DATETIMEFORMAT)
		utcdt_dayS = timezone(tz).localize(dtS).astimezone(utc)
		utcdt_dayE = timezone(tz).localize(dtE).astimezone(utc)
		utc_dayS = utcdt_dayS.strftime(OE_DATETIMEFORMAT)
		utc_dayE = utcdt_dayE.strftime(OE_DATETIMEFORMAT)

		leave_ids = leave_obj.search([
			('state', 'in', ['validate', 'validate1']),
			('employee_id', '=', employee_id),
			('type', '=', 'remove'),
			('date_from', '<=', utc_dayE),
			('date_to', '>=', utc_dayS)
		])
		res = []
		if len(leave_ids) == 0:
			return res

		for leave in leave_ids:
			res.append({
				'code': leave.holiday_status_id.code,
				'tz': tz,
				'start': utc.localize(datetime.strptime(leave.date_from, OE_DATETIMEFORMAT)),
				'end': utc.localize(datetime.strptime(leave.date_to, OE_DATETIMEFORMAT))
			})
		return res


class hr_salary_inputs(models.Model):		
	_name = "hr.salary.inputs"
	_inherit = ['mail.thread']
	
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True,track_visibility='always')
	center_id = fields.Many2one('sos.center', string='Center', related='employee_id.center_id', readonly=False, store=True)
	amount = fields.Float(string='Amount', required=True)
	description = fields.Text('Description')
	date = fields.Date('Effecting Date', required=True,track_visibility='onchange')		
	name = fields.Selection([('SBNS','Bonus of Employee'),('ADV','Advance against Salary'),('ARS','Arrear'),('FINE','Late/Absent Fine'),('LOAN','Personal Loan'), \
							('MOBD','Mobile Deduction'),('TAXD','Tax Deduction'),('RENTD','Rent Deduction'),('FOODD','Food Deduction'),('INSD','Insurance Deduction'), \
							('FAP','Fine and Penalty'),('OD','Other Deduction')],'Category', required=True,track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Paid'),('cancel','Cancelled'),],'Status', default='draft',track_visibility='onchange')
	slip_id =fields.Many2one('hr.payslip', 'Pay Slip', ondelete='cascade',track_visibility='always')
	over_time_hours = fields.Float(string='Over Time Hours',track_visibility='onchange')
	per_hour_rate = fields.Float(string='Per Day Hour Rate',track_visibility='onchange')
	working_days = fields.Float(string='Working Days')
	per_day_rate = fields.Float(string='Per Day Rate')
	#addition	
	loan_line = fields.Many2one('hr.loan.line', string="Loan Line")

	@api.multi
	def inputs_validate(self):
		for rec in self:
			rec.write({'state':'confirm'})
	
	@api.multi
	def inputs_set_draft(self):
		for rec in self:
			rec.write({'state':'draft'})

	@api.multi
	def inputs_cancel(self):
		for rec in self:
			rec.write({'state':'cancel'})

	@api.multi
	def inputs_approve(self):
		for rec in self:
			rec.write({'state':'confirm'})

	@api.multi
	def unlink(self):
		for input_id in self:
			if input_id.state != 'draft':
				raise ValidationError(_('You can only delete Salary Inputs in draft state .'))
		return super(hr_salary_inputs, self).unlink()
																															

class payroll_advice(models.Model):
	_name = 'hr.payroll.advice'
	_description = 'Bank Advice'
	
	@api.model
	@api.depends('line_ids','batch_id')
	def compute_total(self):
		total = 0
		for ln in self.line_ids:
			total += ln.bysal
		self.total = total	

	name = fields.Char('Name', readonly=True, required=True, states={'draft': [('readonly', False)]},)
	note = fields.Text('Description',default='Please make the payroll transfer from above account number to the below mentioned account numbers towards employee salaries:')
	date = fields.Date('Date', readonly=True, required=True, default=lambda * a: time.strftime('%Y-%m-%d'), states={'draft': [('readonly', False)]}, 
		help="Advice Date is used to search Payslips")
	state = fields.Selection([
		    ('draft', 'Draft'),
		    ('confirm', 'Confirmed'),
		    ('cancel', 'Cancelled'),
		], 'Status', index=True, readonly=True, default='draft')
	number = fields.Char('Reference', readonly=True)
	line_ids = fields.One2many('hr.payroll.advice.line', 'advice_id', 'Employee Salary', states={'draft': [('readonly', False)]}, readonly=True, copy=True)
	chaque_nos = fields.Char('Cheque Numbers')
	neft = fields.Boolean('NEFT Transaction', help="Check this box if your company use online transfer for salary")
	company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft': [('readonly', False)]},default=lambda self: self.env.user.company_id)
	bank_id = fields.Many2one('res.partner.bank', 'Bank', readonly=True, states={'draft': [('readonly', False)]}, help="Select the Bank from which the salary is going to be paid")
	batch_id = fields.Many2one('hr.payslip.run', 'Batch', readonly=True,states={'draft': [('readonly', False)]},)
	total = fields.Float('Total',compute='compute_total')
	send_sms = fields.Boolean('Sent SMS?', default=False)
	send_email = fields.Boolean('Sent Email?', default=False)
	
	@api.multi
	def compute_advice(self):
		""" Advice - Create Advice lines in Payment Advice and compute Advice lines."""
		for advice in self:
			old_lines = self.env['hr.payroll.advice.line'].search([('advice_id', '=', advice.id)])
			if old_lines:
				old_lines.unlink()
			#payslips = self.env['hr.payslip'].search([('date_from', '<=', advice.date), ('date_to', '>=', advice.date), ('state', '=', 'done'),('payslip_run_id','=',advice.batch_id.id)])
			payslips = self.env['hr.payslip'].search([('state', '=', 'done'),('payslip_run_id','=',advice.batch_id.id)])
			for slip in payslips:
				#if not slip.employee_id.bank_account_id and not slip.employee_id.bank_account_id.acc_number:
				if not slip.employee_id.bank_id and not slip.employee_id.bankacc:
					raise UserError(_('Please define bank account for the %s employee') % (slip.employee_id.name,))
				payslip_line = self.env['hr.payslip.line'].search([ ('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
				if payslip_line:					
					advice_line = {
						'advice_id': advice.id,
						'name': slip.employee_id.bankacc and slip.employee_id.bankacc or '',
						'employee_id': slip.employee_id.id,
						'bysal': payslip_line.total,
						'slip_id' : slip.id,
					}
					self.env['hr.payroll.advice.line'].create(advice_line)
				slip.advice_id = advice.id
				
	
	#For SOS Staff (Sarfraz)
	@api.multi
	def send_payslip_sms(self):
		for rec in self:
			if rec.batch_id and rec.batch_id.slip_ids:
				for slip in rec.batch_id.slip_ids:
					
					#Here Please Check that SEND SMS is True, if True Then do not Send the SMS,
					if not slip.send_sms:
						text = rec.prepare_message_text(slip)
						message = self.env['send_sms'].render_template(text, 'hr.payslip', slip.id)
						mobile_no = (slip.employee_id.mobile_phone and slip.employee_id.mobile_phone) or (slip.employee_id.work_phone and slip.employee_id.work_phone) or False
						gatewayurl_id = self.env['gateway_setup'].search([('id','=',1)])
						if mobile_no:
							self.env['send_sms'].send_sms_link(message, mobile_no,slip.id,'hr.payslip',gatewayurl_id)
							slip.send_sms = True
							
				rec.send_sms = True	#Advice		
	
	@api.multi
	def prepare_message_text(self,slip=False):
		message = ''
		if slip:
			ttyme = datetime.fromtimestamp(time.mktime(time.strptime(slip.date_to, "%Y-%m-%d")))
			slip_month = (tools.ustr(ttyme.strftime('%B-%Y')))
			
			self.env.cr.execute ("""select sum(abs(ln.total)) as total,cat.name as name from hr_payslip_line ln, hr_salary_rule_category cat where ln.slip_id=%s and ln.category_id = cat.id group by ln.category_id,cat.name order by ln.category_id""" %(slip.id))
			result = self.env.cr.dictfetchall()
			message = "Dear Mr./Ms. " + slip.employee_id.name + ", Your Salary For the Month of " + slip_month + " has been transferred into your Bank Account." + "\n Detail is as "
			for re in result:
				message = message + "\n " + re['name'] + " Salary " + str(re['total'])
			message = message + "\n Regards, SOS"	
		else:
			message = ''
		return message							

	#For SOS Staff (Sarfraz)
	@api.multi
	def send_payslip_email(self):					
		for rec in self:
			if rec.batch_id and rec.batch_id.slip_ids:
				for slip in rec.batch_id.slip_ids:
					if not slip.send_email:
						slip.send_payslip_email()
				rec.send_email = True

	@api.multi
	def confirm_sheet(self):		
		"""confirm Advice - confirmed Advice after computing Advice Lines.."""
		for advice in self:
			if not advice.line_ids:
				raise UserError(_('You can not confirm Payment advice without advice lines.'))
			advice_date = fields.Date.from_string(fields.Date.today())
			advice_year = advice_date.strftime('%m') + '-' + advice_date.strftime('%Y')
			number = self.env['ir.sequence'].next_by_code('payment.advice')
			sequence_num = 'PAY' + '/' + advice_year + '/' + number
			advice.write({
				'number': sequence_num,
				'state': 'confirm'
			})
    
	@api.multi
	def set_to_draft(self):
		self.write({'state':'draft'})

	@api.multi
	def cancel_sheet(self):
		self.write({'state':'cancel'})

	@api.onchange('company_id')
	def onchange_company_id(self):
		self.bank_id = self.company_id.partner_id.bank_ids and self.company_id.partner_id.bank_ids[0].bank_id.id or False


class hr_payslip_run(models.Model):
	_inherit = 'hr.payslip.run'
	_description = 'Payslip Batches'
	
	@api.model
	@api.depends('slip_ids')
	def compute_total(self):
		total = 0
		for slip in self.slip_ids:
			total += slip.total
		self.total = total	
		
	available_advice = fields.Boolean('Made Payment Advice?', help="If this box is checked which means that Payment Advice exists for current batch", 
		readonly=False, copy=False)
	total = fields.Float('Total',compute='compute_total')	

	@api.multi
	def draft_payslip_run(self):
		super(hr_payslip_run, self).draft_payslip_run()
		self.write({'available_advice': False})

	@api.multi
	def create_advice(self):
		for run in self:
			if run.available_advice:
				raise UserError(_("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") % (run.name,))
			company = self.env.user.company_id
			advice_data = {
				'batch_id': run.id,
				'company_id': company.id,
				'name': run.name,
				'date': run.date_end,
				'bank_id': company.partner_id.bank_ids and company.partner_id.bank_ids[0].id or False
			}
			advice = self.env['hr.payroll.advice'].create(advice_data)
			for slip_id in run.slip_ids:
				# TODO is it necessary to interleave the calls ?
				slip_id.action_payslip_done()
				if not slip_id.employee_id.bank_account_id or not slip_id.employee_id.bank_account_id.acc_number:
					raise UserError(_('Please define bank account for the %s employee') % (slip_id.employee_id.name))
				payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', slip_id.id), ('code', '=', 'NET')], limit=1)
				if payslip_line:
					advice_line = {
						'advice_id': advice,
						'name': slip_id.employee_id.bank_account_id.acc_number,
						#'ifsc_code': slip.employee_id.bank_account_id.bank_bic or '',
						'employee_id': slip_id.employee_id.id,
						'bysal': payslip_line.total
					}
					self.env['hr.payroll.advice.line'].create(advice_line)
		self.write({'available_advice' : True})
		
		
class payroll_advice_line(models.Model):
	_name = 'hr.payroll.advice.line'
	_description = 'Bank Advice Lines'

	advice_id = fields.Many2one('hr.payroll.advice', 'Bank Advice')
	name = fields.Char('Bank Account No.', size=25, required=True)
	ifsc_code = fields.Char('IFSC Code', size=16)
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
	bysal = fields.Float('By Salary', digits=dp.get_precision('Payroll'))
	debit_credit = fields.Char('C/D', size=3, required=False,default='C')
	company_id = fields.Many2one('res.company','Company',related='advice_id.company_id', required=False, store=True)
	ifsc = fields.Boolean('IFSC',related='advice_id.neft')
	slip_id = fields.Many2one('hr.payslip', 'Payroll Slip')
	
	@api.onchange('employee_id')
	def onchange_employee_id(self):
		self.name = self.employee_id.bank_account_id.acc_number
		self.ifsc_code = self.employee_id.bank_account_id.bank_bic or ''


class hr_payslip_exception(models.Model):
	_name = 'hr.payslip.exception'
	_description = 'Payroll Exception'

	name = fields.Char('Name', size=256, required=True, readonly=True)
	rule_id = fields.Many2one('hr.payslip.exception.rule', 'Rule', ondelete='cascade',readonly=True)
	slip_id = fields.Many2one('hr.payslip', 'Pay Slip', ondelete='cascade', readonly=True)
	severity = fields.Selection([('low', 'Low'),('medium', 'Medium'),('high', 'High'),('critical', 'Critical'),],
		related='rule_id.severity', string="Severity", store=True,readonly=True)


class hr_payslip_exception_rule(models.Model):
	_name = 'hr.payslip.exception.rule'
	_description = 'Rules describing pay slips in an abnormal state'

	name = fields.Char('Name', size=256, required=True)
	code = fields.Char('Code', size=64, required=True)
	sequence = fields.Integer('Sequence', required=True,help='Use to arrange calculation sequence', index=True,default=5)
	active = fields.Boolean('Active',help="If the active field is set to false, it will allow you to hide the rule without removing it.",default=True)
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get())
	condition_select = fields.Selection([('none', 'Always True'),('python', 'Python Expression')],"Condition Based on",required=True,default='none')
	condition_python = fields.Text('Python Condition',readonly=False,help='The condition that triggers the exception.',default='''
		# Available variables:
				#----------------------
				# payslip: object containing the payslips
				# contract: hr.contract object
				# categories: object containing the computed salary rule categories
						  (sum of amount of all rules belonging to that category).
				# worked_days: object containing the computed worked days
				# inputs: object containing the computed inputs

				# Note: returned value have to be set in the variable 'result'

				result = categories.GROSS.amount > categories.NET.amount
		''')
	severity = fields.Selection([('low', 'Low'),('medium', 'Medium'),('high', 'High'),('critical', 'Critical'),], 'Severity', required=True,default='low')
	note = fields.Text('Description')


	@api.multi
	def satisfy_condition(self,localdict):
		self.ensure_one()
		
		if self.condition_select == 'none':
			return True
		else:  # python code
			try:
				safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
				return 'result' in localdict and localdict['result'] or False
				
			except:
				raise UserError(_('Wrong python condition defined for payroll exception rule %s (%s).') % (self.name, self.code))


class hr_payslip_line(models.Model):
	_name = 'hr.payslip.line'
	_inherit = 'hr.payslip.line'

	@api.one
	@api.depends('quantity','amount','rate')
	def _calculate_total(self):
		self.total = round(float(self.quantity) * self.amount * self.rate / 100,0)

	date_from = fields.Date(related='slip_id.date_from', store=True)
	date_to = fields.Date(related='slip_id.date_to', store=True)
	payslip_run_id = fields.Char('Payslip Batches', related='slip_id.payslip_run_id.name', store=True)
	total = fields.Float(compute='_calculate_total', string='Total',store=True )
