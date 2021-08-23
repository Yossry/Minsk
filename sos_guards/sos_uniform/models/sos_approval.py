import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

import time
import itertools
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class sos_general_approval(models.Model):		
	_name = "sos.general.approval"
	_description = "SOS General Approval"
	_inherit = ['mail.thread']
	_order = "id desc"

	@api.multi
	@api.depends('approval_lines','approval_lines.amount')
	def _compute_total(self):
		for rec in self:
			total = 0
			for line in rec.approval_lines:
				total += line.amount or 0
			rec.total = total

	@api.onchange('state')
	def _compute_status(self):
		if self.state == 'coordinator':
			self.status = 'Approval is Just Entered by the Coordinator'
		elif self.state == 'paid':
			self.status = 'Your Approval is in Account Department From ' + str(self.date)
		elif self.state == 'done':
			self.status = 'Your Approval Completed'	
		elif self.state == 'reject':
			self.status = 'Your Approval is Rejected By ' + self.state + ' on ' + str(self.date)
		else:	
			self.status = 'Your approval is Waiting the Response from ' + self.state + ' Still ' + str(self.date)
	
	name = fields.Char(string='Approval Number', readonly=True)
	employee_id = fields.Many2one('hr.employee', string = "Requested By",domain=[('is_guard','=',False),('active','=',True)], required=True, index= True, readonly=True, states={'coordinator': [('readonly', False)]})
	center_id = fields.Many2one(related='employee_id.center_id', string='Center',store=True, index=True, readonly=True, states={'coordinator': [('readonly', False)]})

	date = fields.Date(string='Requested Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'coordinator': [('readonly', False)]})
	requested_date = fields.Date(string='Requested Date' ,required=True, default=lambda self: datetime.today().strftime('%Y-%m-%d'), readonly=True, states={'coordinator': [('readonly', False)]})
	approved_date = fields.Date(string='Approved Date',readonly=True, states={'coordinator': [('readonly', False)]})
	purpose = fields.Char(string='Purpose',readonly=True, states={'coordinator': [('readonly', False)]})
	beneficiary = fields.Char(string='Beneficiary',readonly=True, states={'coordinator': [('readonly', False)]})

	state = fields.Selection([('coordinator','Coordinator'),('hoc','H.O.C'),('audit_dept','Audit Dept.'),('cfo','CFO'),('mi','M&I Dept.'),('paid','Paid'),('done','Done'),('reject','Rejected')], string='Status', index=True, readonly=True, default='coordinator',track_visibility='always', copy=False,)
	approval_type = fields.Selection([('travelling_adv','Advance Against Travelling'),('salary_adv','Advance against salary'),('expense_adv','Advance against Expenses/Assets'),('loan_request','Loan request'),('expense_claim','Expenses Claim'),('vender_payment','Vendor Payments'),('other','Other')], string='Approval Type', index=True, readonly=True, default='travelling_adv',track_visibility='always', copy=False,)
	total = fields.Float(string='Total',compute='_compute_total',store=True)
	approval_lines = fields.One2many('sos.general.approval.line', 'approval_id', string='Approval Lines') 
	remarks = fields.Text(string='Remarks', track_visibility='onchange', readonly=False, states={'paid': [('readonly', False)],'reject': [('readonly', True)]})
	status = fields.Char('Status', compute='_compute_status')
	move_id = fields.Many2one('account.move', string='Accounting Entry', readonly=True,)

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sos.general.approval')
		result = super(sos_general_approval, self).create(vals)
		return result
	
	@api.one	
	def unlink(self):
		if self.state != 'coordinator':
			raise UserError(('You can not delete Approval which are in Draft State. Please Shift First in  \
							Coordinator state then delete it.'))
		ret = super(sos_general_approval, self).unlink()
		return ret
			
	@api.multi		
	def approval_hoc(self):
		if self.approval_lines:
			self.date = fields.Date.today()
			self.write({'state':'audit_dept'})
		else:
			raise UserError('Please, First Create it Lines')
		
	@api.multi		
	def approval_admin(self):
		self.date = fields.Date.today()
		self.write({'state':'audit_dept'})

	@api.multi		
	def approval_audit_dept(self):
		self.date = fields.Date.today()
		self.write({'state':'cfo'})
		
	@api.multi		
	def approval_cfo(self):
		self.date = fields.Date.today()
		self.write({'state':'paid'})
	
	@api.multi		
	def approval_mi(self):
		self.date = fields.Date.today()
		self.write({'state':'paid'})
	
	@api.multi		
	def approval_paid(self):
		self.date = fields.Date.today()
		self.write({'state':'done'})

	@api.multi		
	def approval_reject(self):
		self.date = fields.Date.today()
		self.write({'state':'reject'})

		
class sos_general_approval_line(models.Model):		
	_name = "sos.general.approval.line"
	_description = "SOS General Approval Lines"
	_inherit = ['mail.thread']
	_order = "id desc"

	approval_id = fields.Many2one('sos.general.approval', string = "Approval", index= True)
	serial = fields.Char('Sr.')
	description = fields.Char('Description')
	amount = fields.Float('Amount')


class AccountMove(models.Model):
	_name = "account.move"
	_inherit = "account.move"
	
	approval_id = fields.Many2one('sos.general.approval', string='Approval')
