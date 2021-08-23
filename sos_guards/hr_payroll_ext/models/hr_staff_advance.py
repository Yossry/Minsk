import pdb
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import math

import logging
_logger = logging.getLogger(__name__)


class hr_staff_advance(models.Model):
	_name = 'hr.staff.advance'
	_inherit = ['mail.thread']
	_description = "Advances To Staff"
	
	name = fields.Char("Description",size=128, required=True, readonly=True, states={'draft': [('readonly',False)]})
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=True, states={'draft': [('readonly',False)]}, track_visibility='onchange')
	date = fields.Date('Date', readonly=True, states={'draft': [('readonly',False)]},default=lambda *a: time.strftime('%Y-%m-%d'), track_visibility='onchange')
	payment_date = fields.Date('Payment Date', readonly=True, states={'draft': [('readonly',False)]}, track_visibility='onchange')
	paid_amount = fields.Float('Paid Amount', digits=(16,2), readonly=True,default=0.0, track_visibility='onchange')
	state = fields.Selection(( ('draft', 'Draft'), ('validate', 'Confirmed'), ('paid', 'Paid'),), 'State', required=True, readonly=True,default='draft', track_visibility='onchange')
	journal_id = fields.Many2one('account.journal', 'Loan Journal', required=True)
	debit_account_id = fields.Many2one('account.account','Debit Account',required=True,readonly=True)
	credit_account_id = fields.Many2one('account.account','Credit Account',required=True,readonly=True)
	move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
	payment_channel = fields.Selection([('bank','Bank'),('cash','Cash')], string='Payment Mode', default='bank', track_visibility='onchange')
	check_number = fields.Char("Check Number")
	note = fields.Text('Note')
		
	@api.multi
	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('You can only delete Entries that are in draft state .'))
		return super(hr_staff_advance, self).unlink()
			
	@api.multi        
	def advance_confirm(self):
		for advance in self:
			advance.write({'state': 'validate'})

	@api.multi        
	def advance_pay(self):
		#if Advance is Being Paid by the Cash then Cash is deducted from the Petty Cash, system do it auto,
		#if Advance is Paid by the Bank the Accounting Entries are Done. OtherWise no Entry.
		
		# do accounting entries here
		move_pool = self.env['account.move']
		timenow = time.strftime('%Y-%m-%d')
		input_obj = self.env['hr.salary.inputs']
		
		model_rec = self.env['ir.model'].search([('model','=','hr.staff.advance')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
				
		for advance in self:

			## Create Entry in hr_salary_inputs
			input_id = input_obj.create({
				'employee_id': advance.employee_id.id,
				'center_id': advance.employee_id.center_id.id,
				'name' : 'ADV',
				'amount' : advance.paid_amount,
				'state' : 'confirm',
				'date' : advance.payment_date or time.strftime('%Y-%m-%d'),
				})
				
			
			##Makeup of Move Data	
			default_partner_id = advance.employee_id.address_home_id.id
			name = _('Advance To Mr. %s') % (advance.employee_id.name)
			move = {
				'narration': name,
				#'date': timenow,
				'date': advance.payment_date or time.strftime('%Y-%m-%d'),
				'journal_id': advance.journal_id.id,
			}            
				        
			amt = advance.paid_amount
			partner_id = default_partner_id
			debit_account_id = advance.debit_account_id.id
			credit_account_id = advance.credit_account_id.id

			line_ids = []
			debit_sum = 0.0
			credit_sum = 0.0
			
			#Debit Entry	        
			if debit_account_id and not advance.payment_channel == 'cash':
				debit_line = (0, 0, {
				    'name': name,
				    'date': advance.payment_date or time.strftime('%Y-%m-%d'),
				    'partner_id': partner_id,
				    'account_id': debit_account_id,
				    'journal_id': advance.journal_id.id,
				    'debit': amt > 0.0 and amt or 0.0,
				    'credit': amt < 0.0 and -amt or 0.0,                    
				})
				line_ids.append(debit_line)
				debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
			
			#Credit Entry if payment mode is not Cash means it is Bank
			if credit_account_id and not advance.payment_channel == 'cash':
				credit_line = (0, 0, {
				    'name': name,
				    'date': advance.payment_date or time.strftime('%Y-%m-%d'),
				    'partner_id': partner_id,
				    'account_id': credit_account_id,
				    'journal_id': advance.journal_id.id,
				    'debit': amt < 0.0 and -amt or 0.0,
				    'credit': amt > 0.0 and amt or 0.0,                    
				})
				line_ids.append(credit_line)
				credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
			
			#Credit Entry If Payment mode is cash means to create entry directly in cashbook
			if credit_account_id and advance.payment_channel == 'cash':
				statement_rec = self.env['account.bank.statement'].search([('date','=',advance.date),('state','=', 'open'),('journal_id','=',7)])
				if statement_rec:
					line_vals = ({
						'statement_id' : statement_rec.id,
						'name' : name,
						'journal_id' : 7,
						'company_id' : 1,
						'date' : advance.payment_date or time.strftime('%Y-%m-%d'),
						'account_id' : debit_account_id,
						'entry_date' : timenow,
						'amount': -amt,
						'a2_id' : self.env['analytic.code'].search([('code','=',advance.employee_id.code), ('name','=',advance.employee_id.name)]).id or False
						})
					statement_line = self.env['account.bank.statement.line'].create(line_vals)
				else:
					raise ValidationError(_('There is no CashBook entry Opened for this Date. May be Cashbook Validated.'))
					
			##Auto Dimensions
			if not advance.payment_channel == 'cash':	
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
				_logger.info('************* Move is Created %r ************', move_id.id)
				advance.move_id = move_id.id,
				_logger.info('********** Move Reference in Advance %r ***********', advance.move_id.id) 
				advance.state = 'paid'
				move_id.post()
			else:
				advance.state = 'paid'	
		return True
		
