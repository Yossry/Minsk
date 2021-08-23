import pdb
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta
import time
import math
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_loans(models.Model):
	_name = 'hr.loans'
	_description = 'Loan Rule'

	name = fields.Char('Name', size=128, required=True)
	code = fields.Char('Code', size=64, required=True,)
	active = fields.Boolean('Active', help="If the active field is set to false, it will allow you to hide the Loan Rule without removing it.",default=True)
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id.id)
	amount_max = fields.Float('Maximum Amount', required=True,)
	shares_max = fields.Float('Maximum Shares', required=True,)
	amount_percentage = fields.Float('(%) of Basic', required=True, help='Share amount of Loan per Payslip should be in the threshold value',default=30.0)
	note = fields.Text('Description')
	journal_id = fields.Many2one('account.journal', 'Loan Journal', required=True)
	salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule')


class hr_loan(models.Model):
	_name = 'hr.loan'
	_description = "Business Loan"

	@api.one
	def _compute_quota(self):
		self.amount_quota = self.amount/self.num_quotas

	@api.one
	@api.depends('amount','paid_amount')
	def _compute_remaining(self):
		self.remaining_debt = self.amount - self.paid_amount
	
	@api.one
	@api.depends('loan_line_ids.paid')		
	def _compute_amount(self):
		total_paid_amount = 0.00
		for loan in self:
			for line in loan.loan_line_ids:
				if line.paid == True:
					total_paid_amount +=line.paid_amount
			
			balance_amount =loan.amount - total_paid_amount
			self.total_amount = loan.amount
			self.balance_amount = balance_amount
			self.paid_amount = loan.amount - balance_amount	

	name = fields.Char("Description",size=128, required=True, readonly=True, states={'draft': [('readonly',False)]})
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly',False)]})
	loan_id = fields.Many2one('hr.loans', 'Loan Category', required=True, readonly=True, states={'draft': [('readonly',False)]})
	amount = fields.Float('Loan Amount', digits=(16,2), required=True, readonly=True, states={'draft': [('readonly',False)]})
	amount_quota = fields.Float(compute='_compute_quota', string='Share Amount', store=False)
	num_quotas = fields.Integer('Number of shares to pay', digits=(16,2), required=True,readonly=True, states={'draft': [('readonly',False)]})
	date_start = fields.Date('Start Date',readonly=True, states={'draft': [('readonly',False)]})
	date_order = fields.Date('Date Order', readonly=True, states={'draft': [('readonly',False)]},default=lambda *a: time.strftime('%Y-%m-%d'))
	date_payment = fields.Date('Date of Payment',readonly=True, states={'draft': [('readonly',False)]})
	paid_quotas = fields.Integer('Shares paid', digits=(16,2), readonly=True,default=0)
	paid_amount = fields.Float('Paid Amount', digits=(16,2), readonly=True,default=0.0)
	total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_amount')
	balance_amount = fields.Float(string="Balance Amount", compute='_compute_amount')
	loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
	remaining_debt = fields.Float(compute='_compute_remaining', string='Balance', store=True)
	active = fields.Boolean('Active',default=True)
	note = fields.Text('Note')
	state = fields.Selection(( ('draft', 'Draft'), ('validate', 'Confirmed'), ('paid', 'Paid'),), 'State', required=True, readonly=True,default='draft')
	#period_id = fields.many2one('account.period', 'Force Period',domain=[('state','<>','done')],states={'draft': [('readonly', False)]}, readonly=True, help="Keep empty to use the period of the validation(Payslip) date.")
	journal_id = fields.Many2one('account.journal',related='loan_id.journal_id', string="Loan Journal")
	debit_account_id = fields.Many2one('account.account','Debit Account',required=True,readonly=True)
	credit_account_id = fields.Many2one('account.account','Credit Account',required=True,readonly=True)
	code = fields.Char(related='loan_id.code', store=True, string="Code")
	move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
	payment_channel = fields.Selection([('bank','Bank'),('cash','Cash')], string='Payment Mode', default='bank')
   
	def _check_dates(self):
		current_date = datetime.now().strftime('%Y-%m-%d')
		for loan in self:
			if loan.date_start < current_date or loan.date_payment:
				return False
		return True

	    
	@api.model
	def create(self,vals):		
		loans = self.env['hr.loans'].browse(vals['loan_id'])
		employee = self.env['hr.employee'].browse(vals['employee_id'])

		if vals['amount'] <= 0 or vals['num_quotas'] <= 0:
			raise UserError('Amount of Loan and the number of Shares to pay should be Greater than Zero')

		if vals['amount'] > loans.amount_max:
			raise UserError(_('Amount of Loan for (%s) is greater than Allowed amount for (%s)') % (employee.name,loans.name))

		if vals['num_quotas'] > loans.shares_max:
			raise UserError(_('Number of Shares for (%s) is greater than Allowed Shares for (%s)') % (employee.name,loans.name))

		amount_quota = vals['amount'] / vals['num_quotas']
		if amount_quota > (employee.contract_id.wage * loans.amount_percentage / 100.0):
			raise UserError(_('The requested Loan Amount for  (%s) Exceed the (%s)%% of his Basic Salary (%s). The Loan cannot be registered') % (employee.name, loans.amount_percentage, employee.contract_id.wage))

		return super(hr_loan, self).create(vals)

	@api.multi        
	def loan_confirm(self):
		self.write({'state': 'validate'})
	
	@api.multi
	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('You can only delete Entries that are in draft state .'))
		return super(hr_loan, self).unlink()	

	@api.multi        
	def loan_pay(self):
		#do accounting entries here
		move_pool = self.env['account.move']
		timenow = time.strftime('%Y-%m-%d')
		model_rec = self.env['ir.model'].search([('model','=','hr.loan')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
				
		for loan in self:
			default_partner_id = loan.employee_id.address_home_id.id
			name = _('Loans To Mr. %s') % (loan.employee_id.name)
			move = {
				'narration': name,
				'date': timenow,
				'journal_id': loan.loan_id.journal_id.id,
			}            
				        
			amt = loan.amount
			partner_id = default_partner_id
			debit_account_id = loan.debit_account_id.id
			credit_account_id = loan.credit_account_id.id

			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
				        
			if debit_account_id:
				debit_line = (0, 0, {
					'name': loan.loan_id.name,
					'date': timenow,
					'partner_id': partner_id,
					'account_id': debit_account_id,
					'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
					'debit': amt > 0.0 and amt or 0.0,
					'credit': amt < 0.0 and -amt or 0.0,                    
				})
				line_ids.append(debit_line)
				debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

			if credit_account_id and not loan.payment_channel == 'cash':
				credit_line = (0, 0, {
					'name': loan.loan_id.name,
					'date': timenow,
					'partner_id': partner_id,
					'account_id': credit_account_id,
					'journal_id': loan.loan_id.journal_id.id or loan.journal_id.id,
					'debit': amt < 0.0 and -amt or 0.0,
					'credit': amt > 0.0 and amt or 0.0,                    
				})
				line_ids.append(credit_line)
				credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
							
			if credit_account_id and loan.payment_channel == 'cash':
				statement_rec = self.env['account.bank.statement'].search([('date','=',loan.date_order),('state','=','open')])
				if statement_rec:
					line_vals = ({
						'statement_id' : statement_rec.id,
						'name' : name,
						'journal_id' : 7,
						'company_id' : 1,
						'date' : loan.date_order,
						'account_id' : debit_account_id,
						'entry_date' : timenow,
						'amount': -amt,
						'a2_id' : self.env['analytic.code'].search([('code','=',loan.employee_id.code), ('name','=',loan.employee_id.name)]).id or False
						})
					statement_line = self.env['account.bank.statement.line'].create(line_vals)
				else:
					raise Warning(_('There is no CashBook entry Opened for this Date. May be Cashbook Validated.'))
			
			
			##Auto Dimensions		
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
			self.write({'move_id': move_id.id, 'state': 'paid'})
			move_id.post()
			self.compute_loan_line()
		return True
	
	@api.multi
	def compute_loan_line(self):
		loan_line = self.env['hr.loan.line']
		input_obj = self.env['hr.salary.inputs']
		
		loan_line.search([('loan_id','=',self.id)]).unlink()
		for loan in self:
			date_start_str = loan.date_payment
			counter = 1
			amount_per_time = loan.amount / loan.num_quotas
			for i in range(1, loan.num_quotas + 1):
				line_id = loan_line.create({
					'paid_date':date_start_str, 
					'paid_amount': amount_per_time,
					'employee_id': loan.employee_id.id,
					'loan_id':loan.id})
				
				## lines creation in hr_salary_inputs
				input_id = input_obj.create({
					'employee_id': loan.employee_id.id,
					'center_id': loan.employee_id.center_id.id,
					'name' : 'LOAN',
					'amount' : amount_per_time,
					'state' : 'confirm',
					'loan_line' : line_id.id,
					'date' : date_start_str + relativedelta.relativedelta(months = 1),
					})
				counter += 1
				date_start_str = date_start_str + relativedelta.relativedelta(months = 1)
		return True				


class hr_loan_line(models.Model):
	_name="hr.loan.line"
	_description = "HR Loan Request Line"
	
	paid_date = fields.Date(string="Payment Date", required=True)
	employee_id = fields.Many2one('hr.employee', string="Employee")
	paid_amount= fields.Float(string="Paid Amount", required=True)
	paid = fields.Boolean(string="Paid")
	notes = fields.Text(string="Notes")
	loan_id =fields.Many2one('hr.loan', string="Loan Ref.", ondelete='cascade')
	payroll_id = fields.Many2one('hr.payslip', string="Payslip Ref.")


class hr_payslip_loan(models.Model):
	_name = 'hr.payslip.loan'
	_description = 'Payslip Loan'
	_order = 'payslip_id, sequence'

	name = fields.Char('Description', size=256, required=True)
	payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade', index=True)
	sequence = fields.Integer('Sequence', required=True, index=True,default=10)
	code = fields.Char('Code', size=52, required=True, help="The code that can be used in the salary rules")
	amount = fields.Float('Amount', default='0.0',help="It is used in computation. For e.g. A rule for sales having 1% commission of basic salary for per product can defined in expression like result = inputs.SALEURO.amount * contract.wage*0.01.")
	contract_id = fields.Many2one('hr.contract', 'Contract', required=True, help="The contract for which applied this input")
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, help="The Employe for which applied this input")


class hr_employee(models.Model):
	_name = 'hr.employee'
	_inherit = 'hr.employee'

	loan_ids = fields.One2many('hr.loan', 'employee_id', 'Employee Loans')

