import json
import pdb
import time
import math
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil import relativedelta



class SOSGuardsPFReturnForm(models.Model):
	_name = "sos.guards.pf.return.form"
	_inherit = ['mail.thread']
	_description = "Guards Provident Fund Returns Form"
	_order = "id"
	
	@api.onchange('code')					
	def onchange_employee(self):
		employee_id = False
		employee_id = self.env['hr.employee'].search([('code','=',self.code)])
		if employee_id:
			self.employee_id = employee_id and employee_id.id or False
			self.cnic = employee_id.cnic and employee_id.cnic or ''
			self.appointment_date = employee_id.appointmentdate and employee_id.appointmentdate or ''
			self.project_id = employee_id.project_id and employee_id.project_id.id or False
			self.center_id = employee_id.center_id and employee_id.center_id.id or False
			self.post_id = employee_id.current_post_id and employee_id.current_post_id.id or False ## here is the Read Access Issue os i use the sudo(), later on i will check it
			self.bank_id = employee_id.bank_id and employee_id.bank_id.id or False
			self.accowner = employee_id.accowner and employee_id.accowner or False
			self.bankacctitle = employee_id.bankacctitle and employee_id.bankacctitle or ''
			self.bankacc = employee_id.bankacc and employee_id.bankacc or ''
			self.termination_date = employee_id.resigdate and employee_id.resigdate or ''
			self.current = employee_id.current
			self.date = fields.Date.today()

	@api.multi
	@api.depends('employee_id','post_id')
	def get_joining_post(self):
		for rec in self:
			joining_post = self.env['sos.guard.post'].search([('employee_id','=',rec.employee_id.id)], order='fromdate', limit=1)
			rec.joining_post = joining_post.post_id.id or False

	name = fields.Char('Name')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee','Employee', required=True)
	code = fields.Char(string='Code',required=True)
	cnic = fields.Char('CNIC')
	current = fields.Boolean('Current')
	date = fields.Date('Date')
	termination_date = fields.Date('Termination Date',track_visibility='onchange')
	appointment_date = fields.Date('Appointment Date',track_visibility='onchange')
	joining_post = fields.Many2one('sos.post', string = 'Joining Post', compute='get_joining_post', store=True)
	bank_id = fields.Many2one('sos.bank',string='Bank Name', required=False)
	bankacctitle = fields.Char(string='Account Title', required=False)
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner')
	bankacc = fields.Char(string='Account No', required=False)
	state = fields.Selection([('draft','Generate Demand'),('verify','Verify'),('approved', 'Approved'),('paid','Paid'),('reject','Rejected') ],'Status',default='draft', track_visibility='onchange')
	line_ids = fields.One2many('sos.guards.pf.return.form.line','pf_return_id','Lines')
	total_deduction = fields.Float('Total Deduction')
	total_employer = fields.Float('Total Employeer Contribution')
	total = fields.Float('Total')
	journal_id = fields.Many2one('account.journal','Journal',default=56)
	debit_account_id = fields.Many2one('account.account','Debit Account',default=334)
	credit_account_id = fields.Many2one('account.account','Credit Account')
	move_id = fields.Many2one('account.move','Journal Entry Ref.')
	remarks = fields.Text('Remarks')
	
	@api.model	
	def create(self,vals):
		#IF Guard is Current, Do not Create the PF Refund Form
		if vals.get('current', False):
			raise UserError('Guard is Currently Active, PF Return can be generated only for Terminated Guards.')

		#Duplication Entry not allowed
		already_exit = self.search([('employee_id','=',vals.get('employee_id')),('state','!=','reject')])
		if already_exit:
				raise UserError("This Guard has already PF refund Form in the System.Duplication is not allowed.")

		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.guards.pf.return.form')
		vals.update({
			'name': st_number,
		})
		new_rec = super(SOSGuardsPFReturnForm, self).create(vals)
		total_deduction = 0
		total_employer_deduction = 0

		#IF Terminated after 3 Months
		diff = 0
		diff = (new_rec.termination_date - new_rec.appointment_date)
		days = diff.days

		if 0 < days < 90:
			new_rec.remarks = "Terminated Within 3 Months"
		if 90 < days < 180:
			new_rec.remarks = "Terminated within 6 Months"
		if days > 180:
			new_rec.remarks = "Terminated After 6 Months"

		if days > 90:
			slip_lines = self.env['guards.payslip.line'].search([('employee_id','=',new_rec.employee_id.id),('code','=','GPROF')], order='date_from')
			if slip_lines:
				for line in slip_lines:
					total_deduction += abs(line.total)
					total_employer_deduction += abs(line.total) if days > 180 else 0
					line_vals = {
						'name' : new_rec.name,
						'employee_id' : new_rec.employee_id.id,
						'slip_id' : line.slip_id and line.slip_id.id or False,
						'number' : line.slip_id and line.slip_id.number or '',
						'slip_line_id' : line.id,
						'slip_date_from' : line.date_from,
						'slip_date_to' : line.date_to,
						'deducted_amount' : abs(line.total),
						'employer_amount' : abs(line.total) if days > 180 else 0,
						'pf_return_id' : new_rec.id,
						'state' : new_rec.state,
					}
					self.env['sos.guards.pf.return.form.line'].create(line_vals)
				new_rec.total_deduction = total_deduction
				new_rec.total_employer = total_employer_deduction
				new_rec.total = new_rec.total_deduction + new_rec.total_employer
		return new_rec
	
	@api.multi
	def unlink(self):
		if self.state == 'draft':
			raise UserError('You can not delete a Record which are in Close State')
		ret = super(SOSGuardsPFReturnForm, self).unlink()
		return ret
				
	@api.multi
	def action_verify(self):
		for rec in self:
			rec.state='verify'
			rec.line_ids.write({'state': 'verify' })
	
	@api.multi
	def action_approved(self):
		for rec in self:
			rec.state='approved'
			rec.line_ids.write({'state': 'approved'})
			
	@api.multi
	def action_paid(self):
		for rec in self:
			move_lines = []
			move_lines.append((0, 0, {
				'name': "Provident Fund Payment of " + rec.code + "-" + rec.employee_id.name,
				'debit': rec.total,
				'credit': 0.0,
				'account_id': rec.debit_account_id and rec.debit_account_id.id or False,
				'journal_id': rec.journal_id and rec.journal_id.id or False,
				'date': fields.Date.today(),
				'a2_id' : rec.employee_id.analytic_code_id and rec.employee_id.analytic_code_id.id or False
			}))

			move_lines.append((0, 0, {
				'name': "Provident Fund Payment of " + rec.code + "-" + rec.employee_id.name,
				'debit': 0,
				'credit': rec.total,
				'account_id': rec.credit_account_id and rec.credit_account_id.id or False,
				'journal_id': rec.journal_id and rec.journal_id.id or False,
				'date': fields.Date.today(),
			}))

			move = {
				'name': rec.name,
				'ref': "Provident Fund Payment of " + rec.code + "-" + rec.employee_id.name,
				'journal_id': rec.journal_id and rec.journal_id.id or False,
				'date': fields.Date.today(),
				'narration': "Provident Fund Payment of " + rec.employee_id.name,
				'line_ids': move_lines,
			}

			move_id = self.env['account.move'].sudo().create(move)
			rec.move_id = move_id and move_id.id or False
			move_id.state = 'posted'
			rec.state='paid'
			rec.line_ids.write({'state': 'paid'})

	@api.multi
	def action_reject(self):
		for rec in self:
			rec.state='reject'
			rec.line_ids.write({'state':'reject'})

	@api.onchange('line_ids')
	def onchange_pf_lines(self):
		total_deduction = 0
		total_employer = 0
		for line in self.line_ids:
			total_deduction +=line.deducted_amount
			total_employer += line.employer_amount
		self.total_deduction = total_deduction
		self.total_employer = total_employer

	@api.onchange('total_deduction','total_employer')
	def onchange_pf_employee_employer_amt(self):
		self.total = self.total_deduction + self.total_employer


class SOSGuardsPFReturnFormLine(models.Model):
	_name = "sos.guards.pf.return.form.line"
	_description = "Guards Provident Fund Return Line Form"

	name = fields.Char('Name')
	employee_id = fields.Many2one('hr.employee','Employee')
	slip_id = fields.Many2one('guards.payslip')
	number = fields.Char('Slip Ref.')
	slip_line_id = fields.Many2one('guards.payslip.line')
	slip_date_from = fields.Date('From Date')
	slip_date_to = fields.Date('To Date')
	deducted_amount = fields.Float('Deducted Amount')
	employer_amount = fields.Float('Employer Amount')
	pf_return_id = fields.Many2one('sos.guards.pf.return.form', 'PF Return Ref.')
	state = fields.Selection([('draft','Generate Demand'),('verify','Verify'),('approved', 'Approved'),('paid','Paid'),('reject','Rejected') ],'Status',default='draft', track_visibility='onchange')