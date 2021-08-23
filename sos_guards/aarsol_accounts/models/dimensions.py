import time
import pdb
from itertools import groupby
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

from odoo.tools import config
from odoo.addons.analytic_structure.MetaAnalytic import MetaAnalytic
import math
import re

import logging
_logger = logging.getLogger(__name__)


def grouplines(self, ordered_lines, sortkey):
	grouped_lines = []
	for key, valuesiter in groupby(ordered_lines, sortkey):
		group = {}
		group['category'] = key
		group['lines'] = list(v for v in valuesiter)

		grouped_lines.append(group)
	return grouped_lines


class res_partner(models.Model, metaclass = MetaAnalytic):
	_inherit = 'res.partner'
	_bound_dimension_id = False
	
	_dimension = {
		'name': 'Partner',
		'column': 'analytic_code_id',
		'ref_module': 'aarsol_accounts',		
	}	


#class project_project(models.Model):
#	_inherit = 'project.project'
#	__metaclass__ = MetaAnalytic
#
#	_dimension = {
#		'name': 'Project',
#		'column': 'analytic_code_id',
#		'ref_module': 'aarsol_accounts',		
#	}


class AssetAsset(models.Model, metaclass = MetaAnalytic):
	_inherit = 'asset.asset'
	
	_dimension = {
		'name': 'Asset',
		'column': 'analytic_code_id',
		'ref_module': 'aarsol_accounts',
	}


class hr_employee(models.Model, metaclass = MetaAnalytic):
	_inherit = 'hr.employee'

	_dimension = {
		'name': 'Employee',
		'column': 'analytic_code_id',
		'ref_module': 'aarsol_accounts',		
	}


class hr_department(models.Model, metaclass = MetaAnalytic):
	_inherit = 'hr.department'
	
	_dimension = {
		'name': 'Department',
		'column': 'analytic_code_id',
		'ref_module': 'aarsol_accounts',		
	}


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	@api.multi
	def finalize_invoice_move_lines(self, move_lines):	
		model_rec = self.env['ir.model'].search([('model','=','account.invoice')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
		
		for move_line in move_lines:	
			if not move_line[2].get('invoice_id',False):	
				move_line[2]['invoice_id'] = self.id			
		
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
				
		return move_lines
	
	
class AccountMove(models.Model):
	_inherit = "account.move"
	_order = 'date desc, name desc, id desc'

	@api.multi
	def post(self, invoice=False):
		if not invoice:
			invoice = self._context.get('invoice', False)
		self._post_validate()
		
		dimension_ok = True		
		for move in self:
			for line in move.line_ids:				
				dimensions = line.account_id.nd_ids
				structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids),('model_name','=','account_move_line')])
				used = [int(structure.ordering) for structure in structures]
				
				
				for n in used:
					if not eval('line.a{}_id'.format(n)):
						n_struct = self.env['analytic.structure'].search([('id','=',n),('model_name','=','account_move_line')])
						_logger.info('.......Dimension ... %r ..............', n_struct.nd_id.name)
						
						raise UserError(_('Please Provide the Dimensions for Account '+line.account_id.code+'-'+line.account_id.name))

			move.line_ids.create_analytic_lines()
			if move.name == '/':
				new_name = False
				journal = move.journal_id

				if invoice and invoice.move_name and invoice.move_name != '/':
					new_name = invoice.move_name
				#elif self._context('payment_ref',False):
				#	new_name = self._context('payment_ref')
				else:
					if journal.sequence_id:
						# If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
						sequence = journal.sequence_id
						if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
							sequence = journal.refund_sequence_id

						#new_name = journal.code + '/' + move.date[0:4] + '/' + sequence.with_context(ir_sequence_date=move.date).next_by_id()[8:]
						new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
					else:
						raise UserError(_('Please define a sequence on the journal.'))

				if new_name:
					move.name = new_name
		return self.write({'state': 'posted'})

	def format_field_name(self, ordering, prefix='a', suffix='id'):		
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)

	
	def line_dimension_lines(self,move_line=None):
		res = []			
		if int(move_line.d_bin):
			size = int(config.get_misc('analytic', 'analytic_size', 10))
			for n in range(1, size + 1):
				if int(move_line.d_bin[size-n]):
					src = self.format_field_name(n,'a','id')	

					structures = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('ordering','=',n)])
					res.append({
						'nd_name': structures.nd_id.name,
						'code': move_line[src].code,
						'name': move_line[src].name,
					})
		return res	


class AccountMoveLine(models.Model, metaclass = MetaAnalytic):
	_inherit = "account.move.line"
	_analytic = True
	_order = "id desc"

	@api.multi
	def dimensions_input(self):
		abc = {
			'name': 'Cost Center and Dimensions',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.dimension.entry',
			'views': [[False, 'form']],
			#'res_id': 1,
			'context': {
				'default_rec_id':self.id,
				'default_model_name':self._name,
				'default_model_db_name': self._name.replace('.', '_'),
				'default_account_id':self.account_id.id,
				'default_readonly':self.move_id.state == 'posted',
			},
			'target': 'new',
		}		
		return abc

	def refresh_dimensions(self):			
		if self.account_id:
			dimensions = self.account_id.nd_ids
			
			structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids)])
			used = [int(structure.ordering) for structure in structures]
			
			number = 0
			size = int(config.get_misc('analytic', 'analytic_size', 10))
			for n in range(1, size + 1):				
				if n in used:
					src_data = 1
					number += math.pow(2,n-1)

			self.d_bin = bin(int(number))[2:].zfill(10)
																						
	def _create_writeoff(self, vals):
		""" Create a writeoff move for the account.move.lines in self. If debit/credit is not specified in vals,
			the writeoff amount will be computed as the sum of amount_residual of the given recordset.

			:param vals: dict containing values suitable fot account_move_line.create(). The data in vals will
				be processed to create bot writeoff acount.move.line and their enclosing account.move.
		"""	
		# Check and complete vals
		if 'account_id' not in vals or 'journal_id' not in vals:
			raise UserError(_("It is mandatory to specify an account and a journal to create a write-off."))
		if ('debit' in vals) ^ ('credit' in vals):
			raise UserError(_("Either pass both debit and credit or none."))
		if 'date' not in vals:
			vals['date'] = self._context.get('date_p') or time.strftime('%Y-%m-%d')
		if 'name' not in vals:
			vals['name'] = self._context.get('comment') or _('Write-Off')
		#compute the writeoff amount if not given
		if 'credit' not in vals and 'debit' not in vals:
			amount = sum([r.amount_residual for r in self])
			vals['credit'] = amount > 0 and amount or 0.0
			vals['debit'] = amount < 0 and abs(amount) or 0.0
		vals['partner_id'] = self.env['res.partner']._find_accounting_partner(self[0].partner_id).id
		company_currency = self[0].account_id.company_id.currency_id
		writeoff_currency = self[0].currency_id or company_currency
		if not self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded' and 'amount_currency' not in vals and writeoff_currency != company_currency:
			vals['currency_id'] = writeoff_currency.id
			sign = 1 if vals['debit'] > 0 else -1
			vals['amount_currency'] = sign * abs(sum([r.amount_residual_currency for r in self]))

		# Writeoff line in the account of self
		first_line_dict = vals.copy()
		first_line_dict['account_id'] = self[0].account_id.id
		if 'analytic_account_id' in vals:
			del vals['analytic_account_id']

		# Writeoff line in specified writeoff account
		second_line_dict = vals.copy()
		second_line_dict['debit'], second_line_dict['credit'] = second_line_dict['credit'], second_line_dict['debit']
		if 'amount_currency' in vals:
			second_line_dict['amount_currency'] = -second_line_dict['amount_currency']

		# ********* These lines are added  ************** #

		model_rec = self.env['ir.model'].search([('model','=','account.move.line.reconcile.writeoff')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')

		number = 0
		nd_ids = eval("self.env['account.account'].browse(second_line_dict.get('account_id')).nd_ids")
		if nd_ids:		
			for auto_entry in auto_entries:
				if auto_entry.dimension_id in nd_ids:
					first_line_dict.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
					ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
					number += math.pow(2,int(ans.ordering)-1)			
			first_line_dict.update({'d_bin' : bin(int(number))[2:].zfill(10)})


		number = 0
		nd_ids = eval("self.env['account.account'].browse(second_line_dict.get('account_id')).nd_ids")
		if nd_ids:		
			for auto_entry in auto_entries:
				if auto_entry.dimension_id in nd_ids:
					second_line_dict.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
					ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
					number += math.pow(2,int(ans.ordering)-1)			
			second_line_dict.update({'d_bin' : bin(int(number))[2:].zfill(10)})

		# *********   end of lines added  ************ #

		# Create the move
		writeoff_move = self.env['account.move'].create({
			'journal_id': vals['journal_id'],
			'date': vals['date'],
			'state': 'draft',
			'line_ids': [(0, 0, first_line_dict), (0, 0, second_line_dict)],
		})
		writeoff_move.post()

		# Return the writeoff move.line which is to be reconciled
		return writeoff_move.line_ids.filtered(lambda r: r.account_id == self[0].account_id)


class AccountBankStatementLine(models.Model, metaclass = MetaAnalytic):
	_inherit = "account.bank.statement.line"
	_analytic = True
	
	@api.one
	@api.depends('d_bin')
	def _get_d_bin(self):
		if self.d_bin:
			self.H10_id = int(self.d_bin[0:1])
			self.H9_id = int(self.d_bin[1:2])
			self.H8_id = int(self.d_bin[2:3])
			self.H7_id = int(self.d_bin[3:4])
			self.H6_id = int(self.d_bin[4:5])
			self.H5_id = int(self.d_bin[5:6])
			self.H4_id = int(self.d_bin[6:7])
			self.H3_id = int(self.d_bin[7:8])
			self.H2_id = int(self.d_bin[8:9])
			self.H1_id = int(self.d_bin[9:10])

	d_bin = fields.Char("Binary Dimension")
	H1_id = fields.Integer(compute='_get_d_bin')
	H2_id = fields.Integer(compute='_get_d_bin')
	H3_id = fields.Integer(compute='_get_d_bin')
	H4_id = fields.Integer(compute='_get_d_bin')
	H5_id = fields.Integer(compute='_get_d_bin')
	H6_id = fields.Integer(compute='_get_d_bin')
	H7_id = fields.Integer(compute='_get_d_bin')
	H8_id = fields.Integer(compute='_get_d_bin')
	H9_id = fields.Integer(compute='_get_d_bin')
	H10_id = fields.Integer(compute='_get_d_bin')

	def format_field_name(self, ordering, prefix='a', suffix='id'):
		"""Return an analytic field's name from its slot, prefix and suffix."""
		return '{pre}{n}_{suf}'.format(pre=prefix, n=ordering, suf=suffix)
																					
	@api.onchange('account_id')
	def _onchange_account_id(self):		
		if self.account_id:
			dimensions = self.account_id.nd_ids
			
			structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids)])
			used = [int(structure.ordering) for structure in structures]
			
			number = 0
			size = int(config.get_misc('analytic', 'analytic_size', 10))
			for n in range(1, size + 1):
				#src = self.format_field_name(n,'H','id')
				if n in used:
					src_data = 1
					number += math.pow(2,n-1)
				#else:
				#	src_data = 0

			self.d_bin = bin(int(number))[2:].zfill(10)		
	
	@api.multi
	def dimensions_input(self):
		abc = {
			'name': 'Cost Center and Dimensions',
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.dimension.entry',
			'views': [[False, 'form']],
			#'res_id': 1,
			'context': {
				'default_rec_id':self.id,
				'default_model_name':self._name,
				'default_model_db_name': self._name.replace('.', '_'),
				'default_account_id':self.account_id.id,
				'default_readonly':self.statement_id.state == 'confirm',
			},
			'target': 'new',
		}		
		return abc
		
	def fast_counterpart_creation(self):
		seq = 10
		for st_line in self:
			# Technical functionality to automatically reconcile by creating a new move line
			vals = {
                'name': st_line.name,
                'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                'credit': st_line.amount > 0 and st_line.amount or 0.0,
                'account_id': st_line.account_id.id,
                'sequence': st_line.amount < 0 and seq or seq + 100
            }
			seq += 1
			account = st_line.account_id
			dimensions = account.nd_ids
			structures = self.env['analytic.structure'].search([('nd_id','in',dimensions.ids),('model_name','=','account_bank_statement_line')])
			used = [int(structure.ordering) for structure in structures]				
			for n in used:
				if not eval('st_line.a{}_id'.format(n)):
					raise UserError(_('Please Provide the Dimensions for Account '+ account.code+'-'+ account.name + '::'+ st_line.name))		    
				vals['a{}_id'.format(n)] = eval('st_line.a{}_id'.format(n)).id
			st_line.process_reconciliation(new_aml_dicts=[vals])
