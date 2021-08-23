import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

DATETIME_FORMAT = "%Y-%m-%d"

class guards_payslip_run(models.Model):
	_name = 'guards.payslip.run'
	_description = 'Payslip Batches'
	_order = 'id desc'
	
	@api.one
	def _get_default_journal(self):
		res = self.env['ir.model.data'].search([('name', '=', 'salary_journal')])
		if res:
			return res.res_id
		return False
	
	name = fields.Char('Name', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]})
	slip_ids = fields.One2many('guards.payslip', 'payslip_run_id', 'Payslips', required=False, readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'),('close', 'Close'),], 'Status', default='draft', readonly=True)
	date_start = fields.Date('Date From', required=True, readonly=True, states={'draft': [('readonly', False)]}, default= lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_end = fields.Date('Date To', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	credit_note = fields.Boolean('Credit Note', readonly=True, states={'draft': [('readonly', False)]}, help="If its checked, indicates that all payslips generated from here are refund payslips.")
	journal_id = fields.Many2one('account.journal', 'Salary Journal', states={'draft': [('readonly', False)]}, readonly=True, required=True, default=_get_default_journal)
	available_advice = fields.Boolean('Made Payment Advice?', default=False, readonly=False, help="If this box is checked which means that Payment Advice exists for current batch")	
	paidon = fields.Boolean('Paidon')
	advice_id = fields.Many2one('guards.payslip.advice', 'Payment Advice')
	
	@api.one
	def copy(self, default=None):
		default = dict(default or {})
		default.update({'available_advice': False})
		return super(guards_payslip_run, self).copy(default)
		
	@api.multi		 
	def draft_payslip_run(self):
		for payslip in self:
			payslip.write({'available_advice': False,'state': 'draft'})
	
	@api.multi		     
	def close_payslip_run(self):
		for payslip in self:
			payslip.write({'state': 'close'})
		return True
			
	@api.multi
	def create_advice(self):
		wf_service = netsvc.LocalService("workflow")
		payslip_pool = self.env['guards.payslip']
		payslip_line_pool = self.env['guards.payslip.line']
		advice_pool = self.env['guards.payroll.advice']
		advice_line_pool = self.env['guards.payroll.advice.line']
		users = self.env.user

		for run in self:
			if run.available_advice:
				raise Warning(_("Payment advice already exists for %s, 'Set to Draft' to create a new advice.") %(run.name))
			
			advice_data = {
				'batch_id': run.id,
				'company_id': users[0].company_id.id,
				'name': run.name,
				'date': run.date_end,
				'bank_id': users.company_id.bank_ids and users.company_id.bank_ids[0].id or False
			}
			advice_id = advice_pool.create(advice_data)
			slip_ids = []
			for slip_id in run.slip_ids:
				wf_service.trg_validate(self.env.uid, 'guards.payslip', slip_id.id, 'guards_verify_sheet', self.env.cr)
				wf_service.trg_validate(self.env.uid, 'guards.payslip', slip_id.id, 'guards_process_sheet', self.env.cr)
				slip_ids.append(slip_id.id)
	
			for slip in payslip_pool.browse(slip_ids):
				line_ids = payslip_line_pool.search([('slip_id', '=', slip.id), ('code', '=', 'NET')])
				if line_ids:
					line = payslip_line_pool.browse(line_ids)
					advice_line = {
						'advice_id': advice_id,
						'name': slip.bankacc or 'No Account Yet',
						'employee_id': slip.employee_id.id,
						'bysal': line.total,
						'slip_id': slip.id,
						'acctitle': slip.bankacctitle or slip.employee_id.name,
					}
				advice_line_pool.create(advice_line)
		slip_ids.write({'advice_id': advice.id})
		return self.write({'available_advice' : True})


class guards_payroll_advice(models.Model):
	_name = 'guards.payroll.advice'
	_description = 'Bank Advice'
	
	@api.depends('line_ids','batch_id')
	def compute_total(self):
		for rec in self:
			total = 0
			for ln in rec.line_ids:
				total += ln.bysal
			rec.total = total	
	
	
	name = fields.Char('Name', size=32, readonly=True, required=True, states={'draft': [('readonly', False)]},)
	note = fields.Text('Description', default="Please make the payroll transfer from above account number to the below mentioned account numbers towards employee salaries:")
	date = fields.Date('Date', readonly=True, required=True, states={'draft': [('readonly', False)]}, default=lambda * a: time.strftime('%Y-%m-%d'), help="Advice Date is used to search Payslips")
	state = fields.Selection([('draft', 'Draft'),('confirm', 'Confirmed'),('cancel', 'Cancelled'),], 'Status', default='draft', readonly=True)
	number = fields.Char('Reference', size=16, readonly=True)
	line_ids = fields.One2many('guards.payroll.advice.line', 'advice_id', 'Employee Salary', states={'draft': [('readonly', False)]}, readonly=True)
	chaque_nos = fields.Char('Cheque Numbers', size=256)
	neft = fields.Boolean('NEFT Transaction', help="Check this box if your company use online transfer for salary")
	company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=1)
	bank_id = fields.Many2one('res.partner.bank', 'Bank', readonly=True, states={'draft': [('readonly', False)]}, help="Select the Bank from which the salary is going to be paid")
	batch_id = fields.Many2one('guards.payslip.run', 'Batch')
	paidon = fields.Boolean('Paid-On', default=False)
	move_id = fields.Many2one('account.move','Accounting Journal')
	total = fields.Float('Total',compute='compute_total')

	@api.multi
	def compute_advice(self):
		"""
		Advice - Create Advice lines in Payment Advice and compute Advice lines.
		"""
		payslip_pool = self.env['guards.payslip']
		advice_line_pool = self.env['guards.payroll.advice.line']
		payslip_line_pool = self.env['guards.payslip.line']
		
		slip_ids=[]
		for advice in self:
			if not advice.batch_id:
				raise UserError(_('Please Select the Payslip Batch'))
				
			old_line_ids = advice_line_pool.search([('advice_id', '=', advice.id)])   
			if old_line_ids:
				old_line_ids.unlink()
			
			for slip in advice.batch_id.slip_ids:
				line = payslip_line_pool.search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
				if line:
					advice_line = {
						'advice_id': advice.id,
						'name': slip.bankacc or 'No Account Yet',
						'employee_id': slip.employee_id.id,
						'bysal': line.total,
						'slip_id': slip.id,
						'acctitle': slip.bankacctitle or slip.employee_id.name,
					}
					advice_line_pool.create(advice_line)
					slip_ids.append(slip.id)
			
			slips = self.env['guards.payslip'].search([('id','in',slip_ids)])
			if slips:		
				slips.write({'advice_id': advice.id})
		return True
	
		
	@api.multi
	def confirm_sheet(self):
		seq_obj = self.env['ir.sequence']
		move_pool = self.env['account.move']
		move_line_pool = self.env['account.move.line']
		for advice in self:
			if not advice.line_ids:
				raise UserError(_('You can not confirm Payment advice without advice lines.'))
			advice_date = datetime.strptime(advice.date, DATETIME_FORMAT)
			advice_year = advice_date.strftime('%m') + '-' + advice_date.strftime('%Y')
			number = seq_obj.get(cr, uid, 'payment.advice')
			sequence_num = 'PAY' + '/' + advice_year + '/' + number
			timenow = time.strftime('%Y-%m-%d')
			
			name = _('Salary Payment of %s') % (advice.name)
			move = {
				'narration': name,
				'date': timenow,
				'ref': sequence_num,
				'journal_id': 24,				
			}

			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			debit_account_id = 13263
			credit_account_id = 13262

			for line in advice.line_ids:
				amt = line.bysal
				emp_id = line.slip_id.employee_id.id

				debit_line = (0, 0, {
					'name': _('Salary Payment of %s') % (line.slip_id.employee_id.name),
					'date': timenow,
					'post_id': line.slip_id.post_id.id,
					'account_id': debit_account_id,
					'journal_id': 24,
					'debit': amt > 0.0 and amt or 0.0,
					'credit': amt < 0.0 and -amt or 0.0,
					'invoice_id': line.slip_id.worked_days_line_ids[0].move_line_id.invoice_id.id,
					'partner_id': line.slip_id.post_id.partner_id.id,
				})
				line_ids.append(debit_line)
				#debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

				credit_line = (0, 0, {
					'name': _('Salary Payment of %s') % (line.slip_id.employee_id.name),
					'date': timenow,
					'post_id': line.slip_id.post_id.id,
					'account_id': credit_account_id,
					'journal_id': 24,
					'debit': amt < 0.0 and -amt or 0.0,
					'credit': amt > 0.0 and amt or 0.0,
					'invoice_id': line.slip_id.worked_days_line_ids[0].move_line_id.invoice_id.id,
					'partner_id': line.slip_id.post_id.partner_id.id,
				})
				line_ids.append(credit_line)
				#credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
			
			move.update({'line_ids': line_ids})
			move_id = move_pool.create(move)
			move = move_id
			
			for line in move.line_ids:
				if line.account_id.id == credit_account_id:
					self.env["account.invoice"].register_payment([line.invoice_id.id],line)
						
			advice.write({'number': sequence_num, 'state': 'confirm','move_id': move_id})
			#if slip.journal_id.entry_posted:
			move.post()				
		return True

	@api.multi
	def unlink(self):
		advice_line_pool = self.env['guards.payroll.advice.line']
		for advice in self:
			line_ids = advice_line_pool.search([('advice_id', '=', advice.id)])   
			if line_ids:
				line_ids.unlink()
			#self.env['guards.payslip.run'].write([advice.batch_id.id], {'available_advice' : False})
			advice.batch_id.write({'available_advice' : False})	
		return super(guards_payroll_advice, self).unlink()
	
	@api.multi	   
	def set_to_draft(self):
		return self.write({'state':'draft'})
		
	@api.multi
	def cancel_sheet(self, cr, uid, ids, context=None):
		return self.write({'state':'cancel'})

class guards_payroll_advice_line(models.Model):
	
	@api.onchange('employee_id')
	def on_change_employee_id(self):
		res = {}
		hr_obj = self.env['hr.employee']
		if not employee_id:
			return {'value': res}
		employee = hr_obj.search([('id','=', employee_id.id)])
		res.update({'name': employee.bank_account_id.acc_number , 'ifsc_code': employee.bank_account_id.bank_bic or ''})
		return {'value': res}

	_name = 'guards.payroll.advice.line'
	_description = 'Bank Advice Lines'
	
	advice_id = fields.Many2one('guards.payroll.advice', 'Bank Advice')
	slip_id = fields.Many2one('guards.payslip', 'Payroll Slip')
	name = fields.Char('Bank Account No.', size=25, required=True)
	acctitle = fields.Char('Account Title', size=50)
	ifsc_code = fields.Char('IFSC Code', size=16)
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True)
	bysal = fields.Float('By Salary')
	debit_credit = fields.Char('C/D', size=3, required=False, default='C')
	company_id = fields.Many2one('res.company', related='advice_id.company_id', required=False, string='Company', store=True)
	ifsc = fields.Boolean(related='advice_id.neft',string='IFSC',store=True)
	
	@api.multi
	def unlink(self):
		payslip_pool = self.env['guards.payslip']
		for advice_line in self:
			advice_line.slip_id.write({'advice_id': False})
		return super(guards_payroll_advice_line, self).unlink()
		
class sos_advances(models.Model):
	_name = 'sos.advances'
	_description = 'SOS Advances'
	
	bankacctitle = fields.Char('Account Title', size=64)
	bankacc = fields.Char('Account No', size=32)
	advice_id = fields.Many2one('guards.payroll.advice', 'Payment Advice')
	amount = fields.Integer('Deduction Amount')

