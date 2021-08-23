import pdb
from odoo.exceptions import UserError, ValidationError
from odoo import tools
from odoo import models, fields, api, _
import math
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta


class sos_guards_salary_difference(models.Model):		
	_name = "sos.guards.salary.difference"
	_inherit = ['mail.thread']
	_description = "SOS Guards Salary Difference"
	
	@api.one
	@api.depends('line_ids','line_ids.amount')
	def _get_total_amount(self):
		total = 0
		for line_id in self.line_ids:
			total += line_id.amount
		self.total = total	
	
	name = fields.Char("Name",required=True)
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	project_id = fields.Many2one('sos.project','Project', default=24,track_visibility='onchange')	
	salary_payable_account = fields.Many2one('account.account','Salary Payable Account',required=True,readonly=True, default=86, track_visibility='onchange')
	expense_account = fields.Many2one('account.account','Expense Account',required=True,readonly=True,default=112,track_visibility='onchange')
	journal_id = fields.Many2one('account.journal','Journal', default=24,track_visibility='onchange')
	move_id = fields.Many2one('account.move','Accounting Entry',readonly=True)
	state = fields.Selection([('draft','Draft'),('validate','Validate'),('paid','Paid')],'Status',default='draft', track_visibility='onchange')
	total = fields.Float(compute='_get_total_amount',string='Total', required=False,store=True)
	line_ids = fields.One2many('sos.guards.salary.difference.line', 'difference_id', 'Lines')
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])
	note = fields.Text('Note')
	
	
	@api.one	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete Record which are not in Draft State. Please Shift First in  Draft state then delete it.'))
		ret = super(sos_guards_salary_difference, self).unlink()
		return ret
		
	@api.one	
	def salary_validate(self):
		self.state = 'validate'
	
	@api.one	
	def salary_paid(self):
		move_obj = self.env['account.move']
		move_lines = []
		timenow = time.strftime('%Y-%m-%d')
		
		model_rec = self.env['ir.model'].search([('model','=','sos.guards.salary.difference')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
		
		name = self.name
		move = {
			'narration': self.name,
			'date': self.date or timenow,
			'journal_id': self.journal_id.id,
		}
		
		
		for rec in self.line_ids:
			debit_line = (0, 0, {
				'name': (_('%s of %s:%s') %(self.name, rec.employee_id.code,rec.employee_id.name)),
				'date': self.date or timenow,
				'account_id': self.expense_account.id,
				'journal_id': self.journal_id.id,
				'debit': rec.amount,
				'credit': 0.0,                    
				})
			
			number = 0
			nd_ids = self.expense_account.nd_ids
			if nd_ids:
				for auto_entry in auto_entries:
					if auto_entry.dimension_id in nd_ids:
						debit_line[2].update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
						ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
						number += math.pow(2,int(ans.ordering)-1)			
				debit_line[2].update({'d_bin' : bin(int(number))[2:].zfill(10)})
				
			move_lines.append(debit_line)
			
			
			credit_line = (0, 0, {
				'name': (_('%s of %s:%s') %(self.name, rec.employee_id.code,rec.employee_id.name)),
				'date': self.date or timenow,
				'journal_id': self.journal_id.id,
				'account_id': self.salary_payable_account.id,
				'debit': 0.0,
				'credit': rec.amount,                 
				})
			
			number = 0
			nd_ids = self.salary_payable_account.nd_ids
			if nd_ids:
				for auto_entry in auto_entries:
					if auto_entry.dimension_id in nd_ids:
						credit_line[2].update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
						ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
						number += math.pow(2,int(ans.ordering)-1)			
				credit_line[2].update({'d_bin' : bin(int(number))[2:].zfill(10)})
				
			move_lines.append(credit_line)
		
		
		move.update({'line_ids': move_lines})
		move = move_obj.create(move)
		self.write({'move_id': move.id, 'state': 'paid'})			
		move.post()
	


class sos_guards_salary_difference_line(models.Model):
	_name = 'sos.guards.salary.difference.line'
	_description = 'Guards Salary Difference Lines'	
	
	
	employee_id = fields.Many2one('hr.employee', 'Guard', required=True)
	amount = fields.Float(string='Amount', required=True)
	difference_id = fields.Many2one('sos.guards.salary.difference','Salary Difference')
