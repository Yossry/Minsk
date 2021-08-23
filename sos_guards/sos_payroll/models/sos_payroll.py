import pdb
import time
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import itertools


class GuardsLeavePolicy(models.Model):
	_name = 'guards.leave.policy'
	_description = 'Guards Leave Policy'
	_order = 'sequence'

	post_id = fields.Many2one('sos.post', 'Post')
	project_id = fields.Many2one('sos.project', 'Project')
	center_id = fields.Many2one('sos.center', 'Center')	
	sequence = fields.Integer('Sequence')
	from_days = fields.Integer("From Days")
	to_days = fields.Integer("To Days")
	leaves = fields.Integer("Leaves")


class hr_salary_rule(models.Model):
	_name = 'hr.salary.rule'
	_inherit = 'hr.salary.rule'
	
	is_loop = fields.Boolean('Repeat')

class guards_contract(models.Model):
	_name = 'guards.contract'
	_inherit = 'guards.contract'

	struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structure',required=True)
	
	#@api.model
	#def get_all_structures(self, contract_ids):
	#	all_structures = []
	#	structure_ids = [contract.struct_id.id for contract in contract_ids]
	#	return list(set(self.env['hr.payroll.structure']._get_parent_structure(structure_ids)))
	
	
	@api.multi
	def get_all_structures(self):
		"""
		@return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
			then first level children and so on) and without duplicata
		"""
		structures = self.mapped('struct_id')
		if not structures:
			return []
		# YTI TODO return browse records
		return list(set(structures._get_parent_structure().ids))

class guards_payslip_worked_days(models.Model):
	_name = 'guards.payslip.worked_days'
	_description = 'Payslip Worked Days'
	_order = 'payslip_id, sequence'

	post_id = fields.Many2one('sos.post', 'Post', required=True, index = True)
	project_id = fields.Many2one('sos.project', 'Project', required=True, index = True)
	center_id = fields.Many2one('sos.center', 'Center', required=True, index = True)
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True, index = True)
	payslip_id = fields.Many2one('guards.payslip', 'Pay Slip', required=True, ondelete='cascade', index = True)
	sequence = fields.Integer('Sequence', required=True)
	code = fields.Selection([('regular','Regular'),('extra','Extra')],'Code')
	number_of_days = fields.Float('Number of Days')
	total_days = fields.Float('Total Days')
	number_of_hours = fields.Float('Number of Hours')
	contract_id = fields.Many2one('guards.contract', 'Contract', required=True, help="The contract for which applied this input", index = True)
	move_line_id = fields.Many2one('account.move.line','Invoice')

class guards_payslip_input(models.Model):
	_name = 'guards.payslip.input'
	_description = 'Payslip Input'
	_order = 'payslip_id, sequence'

	name = fields.Char('Description', size=256, required=True, index= True)
	payslip_id = fields.Many2one('guards.payslip', 'Pay Slip', required=True, ondelete='cascade', index = True)
	sequence = fields.Integer('Sequence', required=True, default=10)
	code = fields.Char('Code', size=52, required=True, help="The code that can be used in the salary rules")
	amount = fields.Float('Amount', default=0.0,help="It is used in computation. For e.g. A rule for sales having 1% commission of basic salary for per product can defined in expression like result = inputs.SALEURO.amount * contract.wage*0.01.")
	contract_id = fields.Many2one('guards.contract', 'Contract', required=True, help="The contract for which applied this input")


class guards_payslip(models.Model):
	_name = 'guards.payslip'
	_inherit = ['mail.thread']
	_description = 'Guards Pay Slip'

	@api.model	
	def _get_default_journal(self):		
		return self.env['account.journal'].search([('name', '=', 'Salary Journal')])

	@api.multi
	@api.depends('line_ids','line_ids.total')
	def _calculate_total(self):
		for rec in self:
			total = 0 
			line_ids = self.env['guards.payslip.line'].search([('slip_id', '=', rec.id), ('code', '=', 'NET')])
			for line in line_ids:
				if line.total:
					total += line.total 
				else:
					total += float(line.quantity) * line.amount
			rec.total = total

	def _get_lines_salary_rule_category(self, cr, uid, ids, field_names, arg=None, context=None):
		result = {}
		if not ids: return result
		for id in ids:
			result.setdefault(id, [])
		cr.execute('''SELECT pl.slip_id, pl.id FROM guards_payslip_line AS pl \
			LEFT JOIN hr_salary_rule_category AS sh on (pl.category_id = sh.id) \
				WHERE pl.slip_id in %s \
				GROUP BY pl.slip_id, pl.sequence, pl.id ORDER BY pl.sequence''',(tuple(ids),))
		res = self.env.cr.fetchall()
		for r in res:
			result[r[0]].append(r[1])
		return result

	struct_id = fields.Many2one('hr.payroll.structure', 'Structure', readonly=True, states={'draft': [('readonly', False)]}, help='Defines the rules that have to be applied to this payslip, accordingly to the contract chosen. If you let empty the field contract, this field isn\'t mandatory anymore and thus the rules applied will be all the rules set on the structure of all contracts of the employee valid for the chosen period')
	name = fields.Char('Description', required=False, readonly=True, states={'draft': [('readonly', False)]})
	number = fields.Char('Reference', required=False, readonly=True, states={'draft': [('readonly', False)]})
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True, readonly=True, states={'draft': [('readonly', False)]}, index = True)
	date_from = fields.Date('Date From', readonly=True, states={'draft': [('readonly', False)]}, required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('Date To', readonly=True, states={'draft': [('readonly', False)]}, required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	state = fields.Selection([('draft', 'Draft'),('verify', 'Waiting'),('done', 'Done'),('cancel', 'Rejected')], 'Status', readonly=True,default='draft', track_visibility='onchange')
	line_ids = fields.One2many('guards.payslip.line', 'slip_id', 'Payslip Lines', readonly=True, states={'draft':[('readonly',False)]})
	company_id = fields.Many2one('res.company', 'Company', required=False, readonly=True, states={'draft': [('readonly', False)]})
	worked_days_line_ids = fields.One2many('guards.payslip.worked_days', 'payslip_id', 'Payslip Worked Days', required=False, readonly=True, states={'draft': [('readonly', False)]})
	input_line_ids = fields.One2many('guards.payslip.input', 'payslip_id', 'Payslip Inputs', required=False, readonly=True, states={'draft': [('readonly', False)]})
	attendance_line_ids = fields.One2many('sos.guard.attendance', 'slip_id', 'Attendance Days')
		
	paid = fields.Boolean('Made Payment Order ? ', required=False, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	note = fields.Text('Description')
	contract_id = fields.Many2one('guards.contract', 'Contract', required=False, readonly=True, states={'draft': [('readonly', False)]})
	credit_note = fields.Boolean('Credit Note', help="Indicates this payslip has a refund of another", readonly=True, states={'draft': [('readonly', False)]},default=False)
	payslip_run_id = fields.Many2one('guards.payslip.run', 'Payslip Batches', readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	paidon = fields.Boolean('Paidon')
	
	journal_id = fields.Many2one('account.journal', 'Salary Journal',states={'draft': [('readonly', False)]}, readonly=True, required=True,default=_get_default_journal)
	move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
	advice_id = fields.Many2one('guards.payroll.advice', 'Bank Advice', track_visibility='onchange')
		
	center_id = fields.Many2one('sos.center','Center', index = True)
	project_id = fields.Many2one('sos.project', string = 'Project', help = 'Project...', index = True)
	post_id = fields.Many2one('sos.post', string = 'Post', help = 'Post...', index = True)
	bank = fields.Many2one('sos.bank','Bank Name',write=['sos.group_bank_account_info'], track_visibility='onchange')
	bankacctitle = fields.Char('Account Title', write=['sos.group_bank_account_info'], track_visibility='onchange')
	bankacc = fields.Char('Account No',write=['sos.group_bank_account_info'], track_visibility='onchange')
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner', write=['sos.group_bank_account_info'], track_visibility='onchange')
	total = fields.Float(compute='_calculate_total', string='Net',store=True)

	abl_incentive = fields.Boolean('ABL Incentive')
	abl_incentive_amt = fields.Integer('ABL Incentive Amount')
	paid_leaves = fields.Integer('Paid Leaves')
	paid_leaves_post = fields.Many2one('sos.post',string='Paid Leaves Post',help='Post...')

	invoice_id = fields.Many2one('account.invoice','Invoice')
	audit_result = fields.Selection([('valid','Valid'),('manual','Manual'),('less','Less'),('more','More')],'Audit Result')
	exit_slip = fields.Boolean('Exit Slip', default=False)
	bank_temp_id = fields.Many2one('sos.bank','Bank Temp Name', help="Storing the bank when salary is being stoped.")
	to_be = fields.Boolean('To Be', default=False)


	#Cron Written to Recompute the Slips
	@api.model
	def may2019_slips(self,nlimit=100):
		recs = False
		recs = self.env['guards.payslip'].search([('to_be','=',True)],limit=nlimit)
		if recs:
			for rec in recs:
				rec.compute_sheet()
				rec.to_be = False

class guards_payslip_line(models.Model):
	_name = 'guards.payslip.line'
	_inherit = 'hr.salary.rule'
	_description = 'Guards Payslip Line'
	_order = 'contract_id, sequence'

	@api.one
	@api.depends('quantity','amount')
	def _calculate_total(self):
		for line in self:
			line.total = float(line.quantity) * line.amount 
	
	slip_id = fields.Many2one('guards.payslip', 'Pay Slip', required=True, ondelete='cascade', index = True)
	post_id = fields.Many2one('sos.post', 'Post', index = True)
	salary_rule_id = fields.Many2one('hr.salary.rule', 'Rule', required=True)
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True, index = True)
	contract_id = fields.Many2one('guards.contract', 'Contract', required=True)
	rate = fields.Float('Rate (%)', default=100.0)
	amount = fields.Float('Amount')
	quantity = fields.Float('Quantity', default=1.0)
	project_id = fields.Many2one('sos.project',related='post_id.project_id',readonly=True, store=True, string='Project',track_visibility='always')
	center_id = fields.Many2one(related='post_id.center_id',store=True, string='Center')
	total = fields.Float(compute='_calculate_total',string='Total', store=True )
	move_line_id = fields.Many2one('account.move.line','Invoice')
		
	date_from = fields.Date(related='slip_id.date_from', store=True, string='Date From')
	date_to = fields.Date(related='slip_id.date_to',store=True, string='Date To')

class hr_employee(models.Model):
	_name ="hr.employee"
	_inherit ='hr.employee'

	slip_ids = fields.One2many('guards.payslip', 'employee_id', 'Payslips', required=False, readonly=True)	
	to_be_processed = fields.Boolean(default=False)

class hr_guard(models.Model):
	_name ="hr.guard"
	_inherit ='hr.guard'

	@api.one
	@api.depends('employee_id.slip_ids')
	def _payslip_count(self):
		employee = self.env['hr.employee'].search([('guard_id','=',self.id)])
		self.payslip_count = self.env['guards.payslip'].search_count([('employee_id', '=', employee.id)])
		self.pf_line_count = self.env['guards.payslip.line'].search_count([('employee_id', '=', employee.id),('code','=','GPROF')])
	
	payslip_count = fields.Integer(compute='_payslip_count',string='Payslips',store=True)
	pf_line_count = fields.Integer(compute='_payslip_count',string='PF Lines')


class sos_post(models.Model):
	_name = 'sos.post'
	_inherit = 'sos.post'
	
	@api.one	
	def _payslip_count(self):
		Payslip = self.env['guards.payslip']
		self.payslip_count = Payslip.search_count([('post_id', '=', self.id)])
		
	payslip_count = fields.Integer(compute='_payslip_count', string='Payslips')
	
class SOSGuardsExitForm(models.Model):
	_name ="sos.guards.exit.form"
	_inherit ='sos.guards.exit.form'

	slip_id = fields.Many2one('guards.payslip', 'Payslip', required=False, readonly=True)
	
	@api.multi
	def guards_payslip_button(self):
		#security_refund = self.env['guards.payslip.line'].search([('employee_id', '=', self.employee_id.id),('date_from', '<', self.date),('code', '=', 'GSDR')])
		#if not security_refund:	
		
		slip = False
		slip = self.env['guards.payslip'].search([('employee_id', '=', self.employee_id.id),('date_from', '<=', self.date),('date_to', '>=', self.date)])
	
		if self.slip_id:
			self.slip_id = False
			self.salary_amt = 0
			self.slip_comments = ''
	
		if not self.slip_id and slip:
			net_amt = 0
			security_refund_amt = 0
			security_amt = 0
			self.slip_id = slip.id or False
	
			security_refund_line = self.env['guards.payslip.line'].search([('slip_id','=',slip.id),('code', '=', 'GSDR')])	
			if security_refund_line:
				security_refund_amt = security_refund_line.total
				self.security_amt = security_refund_amt
			else:
				raise UserError(_("Security Refund is not calculated for this. Please Ask to Recompute the Salary Slip."))	
			
			net_line = self.env['guards.payslip.line'].search([('slip_id','=',slip.id),('code', '=', 'NET')])
			if net_line:
				net_amt = net_line.total or 0
		
			self.salary_amt = net_amt - security_refund_amt or 0
			slip.exit_slip = True
			self.slip_comments = "Slip Found For this Period is attached above link"
		
			# if payslip security refund and total calculated security is not equal.
			security_deposit_line = self.env['guards.payslip.line'].search([('slip_id','=',slip.id),('code', '=', 'GSD')])
			lines = self.env['guards.payslip.line'].search([('employee_id','=',self.employee_id.id),('code','=', 'GSD')])
			if lines:
				amt = 0
				amt = sum(line.total for line in lines)
				security_amt = abs(amt) or 0
				if security_amt != security_refund_amt and security_refund_line:
					self.security_amt = security_amt
					if security_refund_line:
						security_refund_line.total = security_amt
						security_refund_line.amount = security_amt
					if security_deposit_line:
						net_line.total = net_line.total + abs(security_deposit_line.total)
						net_line.amount = net_line.amount + abs(security_deposit_line.amount)
				
					#Change Move Entries
					if security_refund_line and security_deposit_line and slip.move_id:
						move_id = slip.move_id
						move_line = move_id.line_ids.sudo().search([('move_id','=',move_id.id),('account_id','=',168),('debit','>',0)]) ##168 	Security Deposits of Guards
						payable_line = move_id.line_ids.sudo().search([('move_id','=',move_id.id),('account_id','=',86),('credit','>',0),('name' ,'!=', 'Adjustment Entry')])
					
						if move_line and payable_line:
							move_id.state= 'draft'
							if move_line.debit != security_amt:
								move_line.debit = security_amt
								move_line.debit_cash_basis = security_amt
								move_line.balance_cash_basis = security_amt
								move_line.balance = security_amt
							
								#Guards Payable Change 
								payable_line.credit = payable_line.credit + abs(security_deposit_line.total)
								payable_line.amount_residual = payable_line.amount_residual + security_deposit_line.total
								payable_line.balance_cash_basis = payable_line.balance_cash_basis + security_deposit_line.total
								payable_line.credit_cash_basis = payable_line.credit_cash_basis + abs(security_deposit_line.total)
								payable_line.balance = payable_line.balance + security_deposit_line.total
							
							move_id.state= 'posted'		
			
	
		if not self.slip_id and not slip:
			self.slip_comments = "No Slip Found For This Exit Form, Possibilities May Be There Is No Attendance For This Month OR Old Month Exit Form is Entered"	
															
	@api.multi
	def payslip_security_deposite_line(self):
		for rec in self:
			slip = False
			## Handling Slip and Its Lines:
			if rec.slip_id:
				slip = rec.slip_id
			if not slip:
				slip = self.env['guards.payslip'].search([('employee_id', '=', rec.employee_id.id),('date_from', '<=', rec.date),('date_to', '>=', rec.date)])
			if not slip:
				slip = self.env['guards.payslip'].search([('employee_id', '=', rec.employee_id.id)], limit=1, order="id desc")
			if slip:	
				security_return_line = self.env['guards.payslip.line'].search([('slip_id','=',slip.id),('code','=','GSDR')])
				if security_return_line:
					security_return_line.total = rec.security_amt
					security_return_line.amount = rec.security_amt
			
					net_line = self.env['guards.payslip.line'].search([('slip_id','=',slip.id),('code', '=', 'NET')])
					net_line.total = net_line.total + rec.security_amt
					net_line.amount = net_line.amount + rec.security_amt