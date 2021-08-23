import calendar
from dateutil.relativedelta import relativedelta
from pytz import common_timezones, timezone, utc
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
import time
from datetime import date,datetime, timedelta
import math
import pdb
import odoo.netsvc
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from odoo.tools.translate import _
from odoo import tools


class guards_payslip(models.Model):
	_name = 'guards.payslip'
	_inherit = 'guards.payslip'

	#(1)
	@api.model
	def create(self,vals):
		if 'journal_id' in self.env.context:
			vals.update({'journal_id': self.env.context.get('journal_id')})
		slip_id = super(guards_payslip, self).create(vals)

		if len(slip_id.attendance_line_ids) > 0:
			gr = 10
		else:
			if 'attendance_line_ids' in vals:
				att_ids = []
				att_lines = vals['attendance_line_ids']
				for line in att_lines:
					if isinstance(line, (int)):
						att_ids.append(line)
					else:
						att_ids.append(line[1])
				att_ids = list(set(att_ids))
				att_recs = self.env['sos.guard.attendance'].browse(att_ids)
				att_recs.write({'slip_id': slip_id.id})
		return slip_id
	
	#(2)
	@api.multi
	def write(self, vals):
		att_ids = []
		if 'attendance_line_ids' in vals:
			att_lines = vals['attendance_line_ids']
			for line in att_lines:
				if isinstance(line, (int)):
					att_ids.append(line)
				else:
					att_ids.append(line[1])
			att_ids = list(set(att_ids))	
			att_recs = self.env['sos.guard.attendance'].browse(att_ids)
			att_recs.write({'state':'counted'})
		return super(guards_payslip, self).write(vals)
	
	#(3)
	@api.one
	def copy(self, default=None):
		default = dict(default or {})
		company_id = self.env.user.company_id.id
		default.update({
			'line_ids': [],
			'company_id': company_id,
			'number': '',
			'move_id': False,
			'payslip_run_id': False,
			'paid': False,
			'advice_id' : False,
		})
		return super(guards_payslip, self).copy(default)
	
	#(4)
	@api.multi
	def unlink(self):
		for payslip in self:
			if payslip.state not in  ['draft','cancel']:
				raise Warning(_('You cannot delete a payslip which is not draft or cancelled!'))
		return super(guards_payslip, self).unlink()
	
	#(5)
	@api.multi	
	def check_done(self):
		return True
	
	#(6)	
	@api.multi
	@api.constrains('date_from', 'date_to')
	def _check_dates(self):
		for payslip in self:
			if payslip.date_from > payslip.date_to:
				raise ValidationError(_('Payslip Date From: (%s) must be before Date To: (%s)') %(payslip.date_from, payslip.date_to))
		return True
	
	#(7)	
	@api.multi
	def _get_payslips(self):
		att={}
		slip_lines = self.env['guards.payslip.line'].search([('slip_id', 'in', self.ids)])
		for r in slip_lines:
			att[r.slip_id.id] = True
		slip_ids = []
		if att:
			slip_ids = self.env['guards.payslip'].search([('id','=',att.keys())])
		return slip_ids

	#(20)
	@api.onchange('employee_id', 'date_from','date_to')
	def onchange_employee(self):
		if (not self.employee_id) or (not self.date_from) or (not self.date_to):
			return

		self.name = ('Salary Slip of %s for %s') % (self.employee_id.name, tools.ustr(self.date_from.strftime('%B-%Y')))
		self.company_id = self.employee_id.company_id and self.employee_id.company_id.id or False
		self.contract_id = self.employee_id.guard_contract_id and self.employee_id.guard_contract_id.id or False 
		self.struct_id = self.employee_id.guard_contract_id and self.employee_id.guard_contract_id.struct_id.id or False
		self.journal_id = 24
		self.company_id = self.employee_id.company_id and self.employee_id.company_id.id or False
		self.bank = self.employee_id.bank_id and self.employee_id.bank_id.id or False,
		self.bankacctitle = self.employee_id.bankacctitle and self.employee_id.bankacctitle or False
		self.bankacc = self.employee_id.bankacc and self.employee_id.bankacc or False
		self.accowner = self.employee_id.accowner and self.employee_id.accowner or False
		self.paidon = False
		self.post_id = self.employee_id.current_post_id and self.employee_id.current_post_id.id or False
		self.project_id = self.employee_id.project_id and self.employee_id.project_id.id or False
		self.center_id = self.employee_id.center_id and self.employee_id.center_id.id or False
		
		#computation of the salary input
		worked_days_line_ids,abl_incentive,abl_incentive_amt,paid_leaves,paid_leaves_post = self.get_worked_day_lines(self.employee_id, False, self.employee_id.guard_contract_id.id, self.date_from, self.date_to, False)
		attendance_line_ids = self.get_attendance_lines(self.employee_id, self.date_from, self.date_to, paidon=False, exclude_project_ids=False)
		input_line_ids = self.get_inputs(self.employee_id.guard_contract_id.ids, self.date_from, self.date_to, self.employee_id)		
		
		att_ids = []
		if attendance_line_ids:
			for att_line in attendance_line_ids:
				att_ids.append(att_line.id)

		#self.worked_days_line_ids = worked_days_line_ids
		worked_days_lines = self.worked_days_line_ids.browse([])
		for r in worked_days_line_ids:
			worked_days_lines += worked_days_lines.new(r)
		self.worked_days_line_ids = worked_days_lines

		#self.input_line_ids = input_line_ids
		input_lines = self.input_line_ids.browse([])
		for r in input_line_ids:
			input_lines += input_lines.new(r)
		self.input_line_ids = input_lines

		self.attendance_line_ids = att_ids
		self.abl_incentive = abl_incentive
		self.abl_incentive_amt = abl_incentive_amt
		self.paid_leaves = paid_leaves
		self.paid_leaves_post = paid_leaves_post
		return 
		
	#(8)
	@api.multi
	def on_change_employee_id(self, date_from, date_to, employee_id=False, paidon=False, contract_id=False, exclude_project_ids= False):		
		empolyee_obj = self.env['hr.employee']
		contract_obj = self.env['guards.contract']
		worked_days_obj = self.env['guards.payslip.worked_days']
		input_obj = self.env['guards.payslip.input']

		if self.env.context is None:
			self.env.context = {}
		
		#defaults
		res = {
			'value': {
				'line_ids': [],
				#delete old input lines
				'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
				#delete old worked days lines
				'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
				#'details_by_salary_head':[], TODO put me back
				'name':'',
				'contract_id': False,
				'struct_id': False,
				'bank': False,
				'bankacctitle': False,
				'bankacc': False,
				'accowner': False,
				'paidon': paidon,
				}
			}
			
		if (not employee_id) or (not date_from) or (not date_to):
			return res

		employee = empolyee_obj.browse( employee_id)
		res['value'].update({
			'name': _('Salary Slip of %s for %s') % (employee.name, tools.ustr(date_from.strftime('%B-%Y'))),
			'company_id': employee.company_id.id,
			'bank': employee.bank_id.id,
			'bankacctitle': employee.bankacctitle,
			'bankacc': employee.bankacc,
			'accowner': employee.accowner,
			'paidon': paidon,
			'post_id': employee.current_post_id.id,
			'project_id': employee.current_post_id.project_id.id,
			'center_id': employee.current_post_id.center_id.id,
		})
		
		if contract_id:
			contract_ids = [contract_id]
		else:	
			contract_ids = [employee.guard_contract_id.id]
			
		contract_record = contract_obj.browse( contract_ids)[0]
		res['value'].update({
			'contract_id': contract_record and contract_record.id or False
		})
		
		struct_record = contract_record and contract_record.struct_id or False
		if not struct_record:
			return res
		res['value'].update({
			'struct_id': struct_record.id,
		})
		
		#computation of the salary input
		worked_days_line_ids,abl_incentive,abl_incentive_amt,paid_leaves,paid_leaves_post = self.get_worked_day_lines( employee, paidon, contract_record.id, date_from, date_to, exclude_project_ids)
		attendance_line_ids = self.get_attendance_lines(employee, date_from, date_to, paidon, exclude_project_ids)
		input_line_ids = self.get_inputs( contract_ids, date_from, date_to, employee)		
					
		res['value'].update({
			'worked_days_line_ids': worked_days_line_ids,
			'input_line_ids': input_line_ids,
			'attendance_line_ids': attendance_line_ids,
			'abl_incentive': abl_incentive,
			'abl_incentive_amt': abl_incentive_amt,
			'paid_leaves': paid_leaves,
			'paid_leaves_post': paid_leaves_post,
		})
		return res
	
	#(9)
	def on_change_contract_id(self, date_from, date_to, employee_id=False, paidon=False, contract_id=False):
		#TODO it seems to be the mess in the onchanges, we should have onchange_employee => onchange_contract => doing all the things
		if self.env.context is None:
			self.env.context = {}	
				
		contract_obj = self.env['guards.contract']
		res = self.on_change_employee_id(date_from=date_from, date_to=date_to, employee_id=employee_id, paidon=paidon, contract_id=contract_id)
		journal_id = contract_id and contract_obj.browse( contract_id).journal_id.id or False
		res['value'].update({'journal_id': journal_id, 'line_ids': [],})
		
		context = dict(self.env.context)
		context.update({'contract': True})
		if not contract_id:
			res['value'].update({'struct_id': False})
		return res
		
	#(10)
	def update_slip(self, date_from, date_to, employee_id=False, paidon=False, contract_id=False):
		empolyee_obj = self.env['hr.employee']
		worked_days_obj = self.env['guards.payslip.worked_days']
		if self.env.context is None:
			self.env.context = {}
		old_worked_days_ids = self.ids and worked_days_obj.search([('payslip_id', '=', self.ids[0])]) or False
		if old_worked_days_ids:
			sql = "delete from guards_payslip_worked_days where id in %s"
			self.env.cr.execute(sql, (tuple(old_worked_days_ids),))
		employee_id = empolyee_obj.browse(employee_id)
		worked_days_line_ids = self.get_worked_day_lines( employee_id, paidon, contract_id, date_from, date_to)
		for item in worked_days_line_ids:
			item.update({'payslip_id':self.ids[0]})
			worked_days_obj.create(item)

	#(11)	
	@api.multi
	def compute_sheet(self):
		slip_line_pool = self.env['guards.payslip.line']
		sequence_obj = self.env['ir.sequence']
		for payslip in self:
			number = payslip.number or sequence_obj.next_by_code('salary.slip')
			#delete old payslip lines
			payslip.line_ids.unlink()
			#set the list of contract for which the rules have to be applied
			contract_ids = payslip.contract_id.ids or self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
			lines = [(0,0,line) for line in self.get_payslip_lines(payslip.employee_id,contract_ids, payslip.id)]
			payslip.write({'line_ids': lines, 'number': number,})
		return True
		
	#(12)
	#TODO move this function into guards_contract module, on hr.guard object
	@api.one
	def get_contract(self, employee, date_from, date_to):
		contract_obj = self.env['guards.contract']
		clause = []
		#a contract is valid if it ends between the given dates
		clause_1 = ['&',('date_end', '<=', date_to),('date_end','>=', date_from)]
		#OR if it starts between the given dates
		clause_2 = ['&',('date_start', '<=', date_to),('date_start','>=', date_from)]
		#OR if it starts before the date_from and finish after the date_end (or never finish)
		clause_3 = [('date_start','<=', date_from),'|',('date_end', '=', False),('date_end','>=', date_to)]
		#clause_final =  [('employee_id', '=', employee.id),'|','|'] + clause_1 + clause_2 + clause_3
		clause_final =  ['|','|'] + clause_1 + clause_2 + clause_3
		contract_ids = contract_obj.search(clause_final)
		return contract_ids
			
	#(13)
	@api.multi
	def guards_process_sheet(self):
		move_pool = self.env['account.move']
		move_line_pool = self.env['account.move.line']
		att_pool = self.env['sos.guard.attendance']
		arr_pool = self.env['guards.arrears']
		precision = self.env['decimal.precision'].precision_get('Payroll')
		timenow = time.strftime('%Y-%m-%d')
		
		model_rec = self.env['ir.model'].search([('model','=','guards.payslip')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
	
		for slip in self:
			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			date_accounting = slip.date_to
			if slip.move_id:
				continue
			if slip.state == 'done':
				continue

			default_emp_id = slip.employee_id.id
			name = _('Payslip of %s') % (slip.employee_id.name)
			move = {
				'narration': name,
				'date': date_accounting,
				'ref': slip.number,
				'journal_id': slip.journal_id.id,				
			}
			
			for line in slip.line_ids:
				amt = slip.credit_note and -line.total or line.total
				if float_is_zero(amt, precision_digits=precision):
					continue
				emp_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_emp_id
				debit_account_id = line.salary_rule_id.account_debit.id
				credit_account_id = line.salary_rule_id.account_credit.id
				partner_id = line.post_id.partner_id.id if line.salary_rule_id.code == 'BASIC' else False
			
				if debit_account_id:
					debit_line = (0, 0, {
						'name': line.slip_id.name,
						'date': date_accounting,
						'post_id': line.post_id and line.post_id.id or False,
						'account_id': debit_account_id,						
						'journal_id': slip.journal_id.id,
						'debit': abs(amt), #amt > 0.0 and amt or 0.0,
						'credit': 0.0, #amt < 0.0 and -amt or 0.0,
						'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
						'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,						
						'invoice_id': line.move_line_id and line.move_line_id.invoice_id.id or False,
						'partner_id': partner_id,
					})
					line_ids.append(debit_line)
					debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
			
				if credit_account_id:
					credit_line = (0, 0, {
						'name': line.slip_id.name,
						'date': date_accounting,
						'post_id': line.post_id and line.post_id.id or False,
						'account_id': credit_account_id,						
						'journal_id': slip.journal_id.id,
						'debit': 0.0, #amt < 0.0 and -amt or 0.0,
						'credit': abs(amt), #amt > 0.0 and amt or 0.0,
						'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
						'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
						'invoice_id': line.move_line_id and line.move_line_id.invoice_id.id or False,
						'partner_id': partner_id,						
					})
					line_ids.append(credit_line)
					credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
	
			if debit_sum > credit_sum:
				acc_id = slip.journal_id.default_credit_account_id.id
				if not acc_id:
					raise UserError (('The Expense Journal has not properly configured the Credit Account!'))
					
				adjust_credit = (0, 0, {
					'name': _('Adjustment Entry'),
					'date': date_accounting,
					'partner_id': False,
					'account_id': acc_id,
					'journal_id': slip.journal_id.id,
					'debit': 0.0,
					'credit': debit_sum - credit_sum,
				})
				line_ids.append(adjust_credit)
			elif debit_sum < credit_sum:
				acc_id = slip.journal_id.default_debit_account_id.id
				if not acc_id:
					raise UserError (('The Expense Journal has not properly configured the Debit Account!'))
					
				adjust_debit = (0, 0, {
					'name': _('Adjustment Entry'),
					'date': date_accounting,
					'partner_id': False,
					'account_id': acc_id,
					'journal_id': slip.journal_id.id,
					'debit': credit_sum - debit_sum,
					'credit': 0.0,
				})
				line_ids.append(adjust_debit)
				
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
			
			self.write({'move_id': move_id.id})
			move_id.post()
			
			att_ids = att_pool.search([('slip_id','=',slip.id)])
			att_ids.write({'state':'done'})

			arr_ids = arr_pool.search([('employee_id', '=', slip.employee_id.id),('date', '>=', slip.date_from),('date', '<=', slip.date_to),('state', '=', 'confirm')])
			arr_ids.write({'state':'done','slip_id':slip.id})
		return self.write({'paid': True, 'state': 'done'})
	
	#(14)		
	@api.one	
	def guards_cancel_sheet(self):
		if self.state !='draft':
			raise UserError (('Payslip should be in the draft state to Cancel it.'))
		self.state='cancel'
	
	#(15)
	@api.multi
	def guards_verify_sheet(self):
		for sheet in self:		
			sheet.compute_sheet()
			sheet.guards_process_sheet()
	
	#(16)
	@api.multi
	def get_attendance_lines(self,employee, date_from, date_to, paidon, exclude_project_ids):
		att_line_pool = self.env['sos.guard.attendance']
		pending_pool = self.env['project.salary.pending']
		if not employee:
			return False
		set2 = []
		res = []
		if exclude_project_ids:
			set2 = list(set(set2) | set(att_line_pool.search([('paidon','=',paidon), ('name', '>=', date_from), ('name', '<=', date_to), ('employee_id', '=', employee.id),
				('project_id', 'not in', exclude_project_ids.ids),'|',('state','=','counted'),('slip_id','in',self.ids)])))	
		
		att_ids = att_line_pool.search([('paidon','=',paidon), ('name', '>=', date_from), ('name', '<=', date_to),('employee_id', '=', employee.id),'|',('slip_id','=',False),('slip_id','in',self.ids)])
		att_ids = list(set(att_ids) - set(set2))
		return att_ids
	
	#(17)
	@api.multi
	def get_worked_day_lines(self, employee_id, paidon, contract_id, date_from, date_to, exclude_project_ids):
		"""
		@param contract_ids: list of contract id
		@return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
		"""
		
		def was_on_leave(employee_id, datetime_day):
			day = datetime_day.strftime("%Y-%m-%d")
			holiday_ids = self.env['hr.leave'].search([('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
			return holiday_ids and holiday_ids[0].holiday_status_id.name or False
		
		def pending_salary(project_id, day):
			res = False
			pending_ids = self.env['project.salary.pending'].search([('project_id','=',project_id),('state','=','block'),('date_from','<=',day),('date_to','>=',day)])
			if pending_ids:
				res = True
			return res
			
		if self.ids:
			att_obj = self.env['sos.guard.attendance']
			att_ids = att_obj.search([('slip_id','=',self.ids[0])])
		
		result_dict = {}		
		seq = 1
		day_from = date_from
		day_to = date_to
		nb_of_days = (day_to - day_from).days + 1
		
		if exclude_project_ids:
			duty_ids = self.env['sos.guard.attendance'].search([('employee_id','=',employee_id.id),('name', '>=', date_from),('name','<=',date_to),
				('project_id', 'not in', exclude_project_ids.ids),('paidon','=',paidon),'|',('slip_id','=',False),('slip_id','in',self.ids)])
		else:
			duty_ids = self.env['sos.guard.attendance'].search([('employee_id','=',employee_id.id),('name', '>=', date_from),('name','<=',date_to),
				('paidon','=',paidon),'|',('slip_id','=',False),('slip_id','in',self.ids)])

		for duty in duty_ids:
			if duty.action  == 'absent':
				continue
			if duty.action in ('present','double'):
				duty_type='regular'
			else:
				duty_type='extra'
			code = str(duty.post_id.id) + '_' + duty_type

			if not code in result_dict:
				inv = self.env['account.move.line'].search([('post_id', '=', duty.post_id.id),('journal_id','=',1)], order="id desc", limit=1)
				result_dict[code] = {
					'post_id': duty.post_id.id,
					'project_id': duty.project_id.id,
					'center_id': duty.center_id.id,
					'employee_id': employee_id.id,
					'sequence': seq,
					'code': duty_type,
					'number_of_days': 0.0,
					'total_days': nb_of_days,
					'contract_id': contract_id,
					'move_line_id': (paidon and inv and inv[0] ) or False,
				}				
				seq += 1
			if duty.action in ('present','extra'):
				result_dict[code]['number_of_days'] += 1.0
			if duty.action in ('double','extra_double'):
				result_dict[code]['number_of_days'] += 2.0
				
		result = [value for code, value in result_dict.items()]	
		
		paid_leaves = 0
		paid_leaves_post = False
		flag = True
		
		for line in result:
			if flag:
				inner_flag = True
				cnt = 0
			
				paid_ids = self.env['guards.leave.policy'].search([('post_id','=',line['post_id'])], order="from_days desc")
				if not paid_ids:
					paid_ids = self.env['guards.leave.policy'].search([('center_id','=',line['center_id']),('project_id','=',line['project_id']),('post_id','=',False)], order="from_days desc")
				if paid_ids:
					paid_recs = self.env['guards.leave.policy'].browse(paid_ids.ids)
					
					if cnt == 0:
						for ln in result:
							if ln['post_id'] == line['post_id']:
								cnt +=ln['number_of_days']
						## todo Auto paid_leaves_post field is pending for next month (Done)###			
					for paid_rec in paid_recs:
						if cnt >= paid_rec.from_days and inner_flag:
							paid_leaves = paid_rec.leaves or 0
							paid_leaves_post = line['post_id'] or False
							line['number_of_days'] +=  paid_rec.leaves
							inner_flag = False
							flag =False
		abl_incentive = False
		abl_incentive_amt = 0
		return result,abl_incentive,abl_incentive_amt,paid_leaves,paid_leaves_post
	
	#(18)	
	@api.model
	def get_inputs(self, contract_ids, date_from, date_to, employee):
		res = []
		contract_obj = self.env['guards.contract']
		rule_obj = self.env['hr.salary.rule']
		arrears_obj = self.env['guards.arrears']
		contracts = contract_obj.browse(contract_ids)
		structure_ids = contracts.get_all_structures()
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
		inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')
			
		for contract in contracts:					
			for input in inputs:
				arr_amt = ''
				arr_ids = arrears_obj.search([('employee_id', '=', employee.id),('name', '=', input.code),('date', '>=', date_from),('date', '<=', date_to),('state', '=', 'confirm')])
				if arr_ids:
					arr_amt = 0
					for arr_id in arr_ids:
						arr_amt += arr_id.amount
						 
				inputs = {
					'name': input.name,
					'code': input.code,
					'contract_id': contract.id,
					'amount': arr_amt or 0,
					'sequence': 10,
				}
				res += [inputs]		
		return res
	
	#(19)	
	@api.model
	def get_payslip_lines(self, employee_id, contract_ids, payslip_id):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
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
					to_date = datetime.now().strftime('%Y-%m-%d')
				result = 0.0
				self.cr.execute("SELECT sum(amount) as sum\
					FROM guards_payslip as hp, hr_payslip_input as pi \
					WHERE hp.employee_id = %s AND hp.state = 'done' \
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
					(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()[0]
				return res or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = datetime.now().strftime('%Y-%m-%d')
				result = 0.0
				self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
					FROM guards_payslip as hp, guards_payslip_worked_days as pi \
					WHERE hp.employee_id = %s AND hp.state = 'done'\
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
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
					to_date = datetime.now().strftime('%Y-%m-%d')
				self.env.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
					FROM guards_payslip as hp, guards_payslip_line as pl \
					WHERE hp.employee_id = %s AND hp.state = 'done' \
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
					(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()
				return res and res[0] or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules = {}
		categories_dict = {}
		blacklist = []
		payslip_obj = self.env['guards.payslip']
		inputs_obj = self.env['guards.payslip.worked_days']
		obj_rule = self.env['hr.salary.rule']
		
		payslip = payslip_obj.browse(payslip_id)
		worked_days = {}
		
		for worked_days_line in payslip.worked_days_line_ids:
			worked_days['seq'+str(worked_days_line.sequence)] = worked_days_line
		
		inputs = {}
		for input_line in payslip.input_line_ids:
			inputs[input_line.code] = input_line
		
		counter = 1 
		categories_obj = BrowsableObject(payslip.employee_id.id, categories_dict, self.env)
		input_obj = InputLine(payslip.employee_id.id, inputs, self.env)
		worked_days_obj = WorkedDays(payslip.employee_id.id, worked_days, self.env)
		payslip_obj = Payslips(payslip.employee_id.id, payslip, self.env)
		rules_obj = BrowsableObject(payslip.employee_id.id, rules,self.env)

		localdict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj,'counter': counter}
		#get the ids of the structures on the contracts and their parent id as well
		contracts = self.env['guards.contract'].browse(contract_ids)
		structure_ids = contracts.get_all_structures()
		#get the rules of the structure and thier children
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

		for contract in contracts:
			employee = employee_id
			localdict.update({'employee': employee, 'contract': contract})
			for rule in obj_rule.browse(sorted_rule_ids):
				if rule.is_loop:					
					while counter <= len(worked_days):
						key = rule.code + '-' + str(contract.id) + '-' + str(counter)
						localdict['result'] = None
						localdict['result_qty'] = 1.0
						#check if the rule can be applied
						if rule._satisfy_condition(localdict) and rule.id not in blacklist:
							#compute the amount of the rule
							amount, qty, rate = rule._compute_rule(localdict)
							#check if there is already a rule computed with that code
							previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
							#set/overwrite the amount computed for this rule in the localdict
							tot_rule = previous_amount + amount * qty 
							localdict[rule.code] = tot_rule
							rules[rule.code] = rule
							#sum the amount for its salary category
							localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
							#create/overwrite the rule in the temporary results
							
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
								'employee_id': payslip.employee_id.id,
								'quantity': qty,
								'rate': rate,
								'post_id': worked_days['seq'+str(counter)].post_id.id,
								'move_line_id': worked_days['seq'+str(counter)].move_line_id and worked_days['seq'+str(counter)].move_line_id.id,
							}
							counter += 1
							localdict['counter'] = counter
						else:
							#blacklist this rule and its children
							blacklist += [id for id, seq in rule._recursive_search_of_rules()]
				else:
					key = rule.code + '-' + str(contract.id)
					localdict['result'] = None
					localdict['result_qty'] = 1.0
					localdict['result_rate'] = None
					#check if the rule can be applied
					if rule._satisfy_condition(localdict) and rule.id not in blacklist:
						#compute the amount of the rule
						
						amount, qty, rate = rule._compute_rule(localdict)
						#check if there is already a rule computed with that code
						previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
						#set/overwrite the amount computed for this rule in the localdict
						
						tot_rule = amount * qty * rate / 100.0
						localdict[rule.code] = tot_rule
						rules[rule.code] = rule
						#sum the amount for its salary category
						localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
						#create/overwrite the rule in the temporary results
					
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
							'employee_id': payslip.employee_id.id,
							'post_id': payslip.employee_id.current_post_id.id,
							'quantity': qty,
							'rate': rate,
					
						}
					
					else:
						#blacklist this rule and its children
						blacklist += [id for id, seq in rule._recursive_search_of_rules()]				
		result = [value for code, value in result_dict.items()]
		return result


class guards_arrears(models.Model):		
	_name = "guards.arrears"
	_inherit = ['mail.thread']
	
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True, track_visibility='onchange')
	center_id = fields.Many2one('sos.center', string='Center', related='employee_id.center_id', readonly=False, store=True, ondelete='restrict', track_visibility='onchange')
	amount = fields.Float(string='Amount', required=True, track_visibility='onchange')
	description = fields.Text('Description', track_visibility='onchange')
	date = fields.Date('Period', required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), track_visibility='onchange')		
	name = fields.Selection([('BNS','Bonus of Employee'),('ADV','Advance against Salary'),('ARS','Arrear'),('FINE','Fine Deduction'),('GLD','Guard Loan Deduction'),('GSD','Guard Security Deduction'),('EXSP','Excess Salary Paid'),('MBLD','MBL Deduction'),],'Category', required=True, track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Paid'),('cancel','Cancelled'),],'Status',default='draft',track_visibility='onchange')
	slip_id =fields.Many2one('guards.payslip', 'Pay Slip', ondelete='cascade')
	bank_id = fields.Many2one('sos.bank', string='Bank', related='employee_id.bank_id', store=True)
	to_be = fields.Boolean('To Be')

	@api.multi
	def arrears_validate(self):
		for arrear in self:		
			arrear.state='confirm'

	@api.multi
	def arrears_cancel(self):			
		for arrear in self:		
			arrear.state='cancel'

	@api.multi
	def arrear_approve(self):
		for arrear in self:		
			arrear.state='confirm'

	#Cron Jobs
	@api.model
	def process_old_arrear_entry(self, nlimit=100):
		arrears = self.search([('to_be','=',True)],limit=nlimit)
		if arrears:
			for arr in arrears:
				slip_id = self.env['guards.payslip'].search([('employee_id','=',arr.employee_id.id),('date_from','<=',arr.date),('date_to','>=',arr.date)], order='date_from')
				if slip_id:
					slip = slip_id[0]
					arr.slip_id = slip.id
					arr.to_be = False



class project_salary_pending(models.Model):		
	_name = "project.salary.pending"
	_description = 'Pending Salaries of Project'
		
	project_id = fields.Many2one('sos.project', string='Poject', required=True, readonly=False, ondelete='restrict')
	name = fields.Text('Description')
	date_from = fields.Date('Date From', readonly=True, states={'draft': [('readonly', False)]}, required=True)
	date_to = fields.Date('Date To', readonly=True, states={'draft': [('readonly', False)]}, required=True)
	state = fields.Selection([('draft','Draft'),('block','Block'),('open','Open')],'Status',default='draft')
	
	### Pending OPen Function  ###
	@api.multi
	def pending_open(self):		
		for p in self:		
			p.state='open'
		for rec in self:
			sql="""select distinct employee_id from sos_guard_attendance where project_id = %s and name >= %s and name <= %s"""
			self.env.cr.execute(sql,(rec.project_id.id,rec.date_from,rec.date_to))		
			res= self.env.cr.dictfetchall()
			for emp in res:
				self.env['hr.guard']._check_draft_attendance(emp['employee_id'])
	
	### Pending Block Function  ###
	@api.multi			
	def pending_block(self):
		for p in self:
			p.state='block'	
		for rec in self:
			sql="""select distinct employee_id from sos_guard_attendance where project_id = %s and name >= %s and name <= %s"""
			self.env.cr.execute(sql,(rec.project_id.id,rec.date_from,rec.date_to))
			res= self.env.cr.dictfetchall()
			for emp in res:
				self.env['hr.guard']._check_draft_attendance(emp['employee_id'])

class guards_payroll_advice(models.Model):
	_inherit = 'guards.payroll.advice'
	
	#advice should bd batch name plus bank name
	@api.model
	def create(self, vals):
		if vals.get('batch_id',False):
			batch_rec = self.env['guards.payslip.run'].search([('id','=',vals['batch_id'])])
			bank_id =  vals.get('bank_id',False)
			if batch_rec:
				batch_name = batch_rec.name or ''
			else:	
				batch_name =''
			
			if bank_id:
				bank_rec =  self.env['res.partner.bank'].search([('id','=',bank_id)])
				bank_name = (bank_rec.bank_id and bank_rec.bank_id.name) or (bank_rec.acc_number and bank_rec.acc_number) or ''
			else:
				bank_name = ''		
			
			vals['name'] = batch_name + '/' + bank_name
		result = super(guards_payroll_advice, self).create(vals)
		return result
	
