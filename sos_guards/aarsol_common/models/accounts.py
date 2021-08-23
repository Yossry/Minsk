import time
import pdb
from odoo.osv import expression
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from itertools import groupby
#from odoo.tools import pycompat    by farooq
import base64

import odoo.tools as tools
from odoo import http
from odoo.addons.web.controllers import main as report
import json
import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
#from odoo.tools import html_escape, pycompat      by farooq
from odoo.tools.safe_eval import safe_eval

    
def grouplines(self, ordered_lines, sortkey):
	grouped_lines = []
	for key, valuesiter in groupby(ordered_lines, sortkey):
		group = {}
		group['category'] = key
		group['lines'] = list(v for v in valuesiter)

		grouped_lines.append(group)
	return grouped_lines


class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.multi
	@api.depends('name','code')	
	def name_get(self):
		result = []
		for partner in self:
			name = partner.name
			if partner.code:
				name = partner.code + '-' + name
			result.append((partner.id, name))
		return result 

	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []		
		if name:
			domain = ['|',('code', '=ilike', '%' + name + '%'),('name', operator, name)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		recs = self.search(domain + args, limit=limit)
		return recs.name_get()


class AccountSection(models.Model):
	_name = "account.section"
	_description = "Account Sections"

	code = fields.Char('Section Code',translate=True)
	name = fields.Char('Section Name',required=True,translate=True)
	parent_id = fields.Many2one('account.section','Parent Section')

	@api.multi
	@api.depends('code', 'name')
	def name_get(self):
		result = []
		for line in self:
			result.append((line.id, (line.code or '') + ' - ' + (line.name or '')))			
		return result
		
	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []		
		if name:
			domain = ['|',('code', '=ilike', '%' + name + '%'),('name', operator, name)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		recs = self.search(domain + args, limit=limit)
		return recs.name_get()	


class AccountAccount(models.Model):
	_inherit = 'account.account'
	_rec_name = 'code'

	account_section = fields.Many2one('account.section','Account Section')


class AccountJournal(models.Model):
	_inherit = 'account.journal'	

	combine_entry = fields.Boolean('One Combined Entry.')


class AccountMove(models.Model):
	_inherit = "account.move"
	_order = 'date desc, name desc, id desc'

	@api.multi
	def write(self, vals):
		res = True
		if 'ref' in vals and not vals['ref']:
			del vals['ref']
		if 'line_ids' in vals:
			res = super(AccountMove, self.with_context(check_move_validity=False)).write(vals)
			self.assert_balanced()
		elif vals:
			res = super(AccountMove, self).write(vals)
		return res

	@api.multi
	def post(self, invoice=False):
		if not invoice:
			invoice = self._context.get('invoice', False)
		self._post_validate()
		
		for move in self:
			
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

	def move_layout_lines(self,move_id=None):		
		move_lines = self.browse(move_id).line_ids
		sortkey = lambda x: x.section_id if x.section_id else ''
		return grouplines(self, move_lines, sortkey)

	@api.multi
	def assert_balanced(self):
		return True
	
	voucher_type = fields.Selection([('general', 'General Voucher'), ('payment', 'Payment Voucher'),('receipt', 'Receipt Voucher'),
		('stock', 'Stock Voucher'), ('asset', 'Asset Voucher')], string='Voucher Type')	
		
	statement_id = fields.Many2one('account.bank.statement')
	voucher_seq = fields.Integer('VSeq')	


class AccountMoveLine(models.Model):
	_inherit = "account.move.line"
	_order = "id desc"

	@api.model
	def _get_company(self):		
		context = dict(self._context or {})
		company_id = context.get('company_id', False)
		if company_id:
			return company_id
	
	company_id = fields.Many2one('res.company', related='move_id.company_id', string='Company', store=True,default=_get_company)
	section_id = fields.Many2one('account.move.line.section','Section')	
	sequence = fields.Integer(string='Sequence', default=10)
	
	@api.multi
	@api.depends('move_id')
	def name_get(self):
		result = []
		for line in self:
			if line.debit:
				result.append((line.id, (line.move_id.name if line.move_id.name else '') + ':' + line.name if line.name else '' + '(' + (str(line.debit) if line.debit else '') + ')'))
			else:
				result.append((line.id, (line.move_id.name if line.move_id.name else '') + ':' + line.name if line.name else '' + '(' + (str(line.credit) if line.credit else '') + ')'))
		return result


class AccountBankStatementLine(models.Model):
	_inherit = "account.bank.statement.line"
	
	voucher_seq = fields.Integer('V',default=1)
		
	def _prepare_reconciliation_move(self, move_ref):
		data = super(AccountBankStatementLine, self)._prepare_reconciliation_move(move_ref)
		data['statement_id'] = self.statement_id.id
		data['voucher_seq'] = self.voucher_seq
				
		return data
	
	def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
		""" Match statement lines with existing payments (eg. checks) and/or payables/receivables (eg. invoices and credit notes) and/or new move lines (eg. write-offs).
			If any new journal item needs to be created (via new_aml_dicts or counterpart_aml_dicts), a new journal entry will be created and will contain those
			items, as well as a journal item for the bank statement line.
			Finally, mark the statement line as reconciled by putting the matched moves ids in the column journal_entry_ids.

			:param self: browse collection of records that are supposed to have no accounting entries already linked.
			:param (list of dicts) counterpart_aml_dicts: move lines to create to reconcile with existing payables/receivables.
				The expected keys are :
				- 'name'
				- 'debit'
				- 'credit'
				- 'move_line'
				    # The move line to reconcile (partially if specified debit/credit is lower than move line's credit/debit)

			:param (list of recordsets) payment_aml_rec: recordset move lines representing existing payments (which are already fully reconciled)

			:param (list of dicts) new_aml_dicts: move lines to create. The expected keys are :
				- 'name'
				- 'debit'
				- 'credit'
				- 'account_id'
				- (optional) 'tax_ids'
				- (optional) Other account.move.line fields like analytic_account_id or analytics_id

			:returns: The journal entries with which the transaction was matched. If there was at least an entry in counterpart_aml_dicts or new_aml_dicts, this list contains
				the move created by the reconciliation, containing entries for the statement.line (1), the counterpart move lines (0..*) and the new move lines (0..*).
		"""
		counterpart_aml_dicts = counterpart_aml_dicts or []
		payment_aml_rec = payment_aml_rec or self.env['account.move.line']
		new_aml_dicts = new_aml_dicts or []

		aml_obj = self.env['account.move.line']

		company_currency = self.journal_id.company_id.currency_id
		statement_currency = self.journal_id.currency_id or company_currency
		st_line_currency = self.currency_id or statement_currency

		counterpart_moves = self.env['account.move']

		# Check and prepare received data
		if any(rec.statement_id for rec in payment_aml_rec):
			raise UserError(_('A selected move line was already reconciled.'))
		for aml_dict in counterpart_aml_dicts:
			if aml_dict['move_line'].reconciled:
				raise UserError(_('A selected move line was already reconciled.'))
			if isinstance(aml_dict['move_line'], pycompat.integer_types):
				aml_dict['move_line'] = aml_obj.browse(aml_dict['move_line'])
		for aml_dict in (counterpart_aml_dicts + new_aml_dicts):
			if aml_dict.get('tax_ids') and isinstance(aml_dict['tax_ids'][0], pycompat.integer_types):
				# Transform the value in the format required for One2many and Many2many fields
				aml_dict['tax_ids'] = [(4, id, None) for id in aml_dict['tax_ids']]
		if any(line.journal_entry_ids for line in self):
			raise UserError(_('A selected statement line was already reconciled with an account move.'))

		# Fully reconciled moves are just linked to the bank statement
		total = self.amount
		for aml_rec in payment_aml_rec:
			total -= aml_rec.debit - aml_rec.credit
			aml_rec.with_context(check_move_validity=False).write({'statement_line_id': self.id})
			counterpart_moves = (counterpart_moves | aml_rec.move_id)

		# Create move line(s). Either matching an existing journal entry (eg. invoice), in which
		# case we reconcile the existing and the new move lines together, or being a write-off.
		if counterpart_aml_dicts or new_aml_dicts:
			st_line_currency = self.currency_id or statement_currency
			st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False

			# Create the move
			self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
			move_vals = self._prepare_reconciliation_move(self.statement_id.name)	
			
			######################  Added search line and make create conditional      #############################
			#move = self.env['account.move'].create(move_vals)
			move = self.env['account.move'].search([('statement_id','=',move_vals['statement_id']),('voucher_seq','=',move_vals['voucher_seq'])])
			if not move:
				move = self.env['account.move'].create(move_vals)
			################   End Change        #############################
			
			counterpart_moves = (counterpart_moves | move)

			# Create The payment
			payment = self.env['account.payment']
			if abs(total)>0.00001:
				partner_id = self.partner_id and self.partner_id.id or False
				partner_type = False
				if partner_id:
					if total < 0:
						partner_type = 'supplier'
					else:
						partner_type = 'customer'

				payment_methods = (total>0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
				currency = self.journal_id.currency_id or self.company_id.currency_id
				payment = self.env['account.payment'].create({
					'payment_method_id': payment_methods and payment_methods[0].id or False,
					'payment_type': total >0 and 'inbound' or 'outbound',
					'partner_id': self.partner_id and self.partner_id.id or False,
					'partner_type': partner_type,
					'journal_id': self.statement_id.journal_id.id,
					'payment_date': self.date,
					'state': 'reconciled',
					'currency_id': currency.id,
					'amount': abs(total),
					'communication': self._get_communication(payment_methods[0] if payment_methods else False),
					'name': self.statement_id.name,
				})

			# Complete dicts to create both counterpart move lines and write-offs
			to_create = (counterpart_aml_dicts + new_aml_dicts)
			ctx = dict(self._context, date=self.date)
			for aml_dict in to_create:
				aml_dict['move_id'] = move.id
				aml_dict['partner_id'] = self.partner_id.id
				aml_dict['statement_line_id'] = self.id
				if st_line_currency.id != company_currency.id:
					aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict['credit']
					aml_dict['currency_id'] = st_line_currency.id
					if self.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
						# Statement is in company currency but the transaction is in foreign currency
						aml_dict['debit'] = company_currency.round(aml_dict['debit'] / st_line_currency_rate)
						aml_dict['credit'] = company_currency.round(aml_dict['credit'] / st_line_currency_rate)
					elif self.currency_id and st_line_currency_rate:
						# Statement is in foreign currency and the transaction is in another one
						aml_dict['debit'] = statement_currency.with_context(ctx).compute(aml_dict['debit'] / st_line_currency_rate, company_currency)
						aml_dict['credit'] = statement_currency.with_context(ctx).compute(aml_dict['credit'] / st_line_currency_rate, company_currency)
					else:
						# Statement is in foreign currency and no extra currency is given for the transaction
						aml_dict['debit'] = st_line_currency.with_context(ctx).compute(aml_dict['debit'], company_currency)
						aml_dict['credit'] = st_line_currency.with_context(ctx).compute(aml_dict['credit'], company_currency)
				elif statement_currency.id != company_currency.id:
					# Statement is in foreign currency but the transaction is in company currency
					prorata_factor = (aml_dict['debit'] - aml_dict['credit']) / self.amount_currency
					aml_dict['amount_currency'] = prorata_factor * self.amount
					aml_dict['currency_id'] = statement_currency.id

			# Create write-offs
			# When we register a payment on an invoice, the write-off line contains the amount
			# currency if all related invoices have the same currency. We apply the same logic in
			# the manual reconciliation.
			counterpart_aml = self.env['account.move.line']
			for aml_dict in counterpart_aml_dicts:
				counterpart_aml |= aml_dict.get('move_line', self.env['account.move.line'])
			new_aml_currency = False
			if counterpart_aml\
					and len(counterpart_aml.mapped('currency_id')) == 1\
					and counterpart_aml[0].currency_id\
					and counterpart_aml[0].currency_id != company_currency:
				new_aml_currency = counterpart_aml[0].currency_id
			for aml_dict in new_aml_dicts:
				aml_dict['payment_id'] = payment and payment.id or False
				if new_aml_currency and not aml_dict.get('currency_id'):
					aml_dict['currency_id'] = new_aml_currency.id
					aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], new_aml_currency)
				aml_obj.with_context(check_move_validity=False, apply_taxes=True).create(aml_dict)

			# Create counterpart move lines and reconcile them
			for aml_dict in counterpart_aml_dicts:
				if aml_dict['move_line'].partner_id.id:
					aml_dict['partner_id'] = aml_dict['move_line'].partner_id.id
				aml_dict['account_id'] = aml_dict['move_line'].account_id.id
				aml_dict['payment_id'] = payment and payment.id or False

				counterpart_move_line = aml_dict.pop('move_line')
				if counterpart_move_line.currency_id and counterpart_move_line.currency_id != company_currency and not aml_dict.get('currency_id'):
					aml_dict['currency_id'] = counterpart_move_line.currency_id.id
					aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(aml_dict['debit'] - aml_dict['credit'], counterpart_move_line.currency_id)
				new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)

				(new_aml | counterpart_move_line).reconcile()

			# Balance the move
			st_line_amount = -sum([x.balance for x in move.line_ids])
			aml_dict = self._prepare_reconciliation_move_line(move, st_line_amount)
			aml_dict['payment_id'] = payment and payment.id or False
			aml_obj.with_context(check_move_validity=False).create(aml_dict)

			#################### Remarked Post Call ############################
			#move.post()
			#record the move name on the statement line to be able to retrieve it in case of unreconciliation
			self.write({'move_name': move.name})
			payment and payment.write({'payment_reference': move.name})
		elif self.move_name:
			raise UserError(_('Operation not allowed. Since your statement line already received a number, you cannot reconcile it entirely with existing journal entries otherwise it would make a gap in the numbering. You should book an entry and make a regular revert of it in case you want to cancel it.'))
		counterpart_moves.assert_balanced()
		return counterpart_moves


class account_move_line_section(models.Model):
	_name = "account.move.line.section"
	_description = "Accoun Move Line Sections"

	name = fields.Char('Section')
	code = fields.Char('Code')
	sequence = fields.Integer('Sequence')
	separator = fields.Boolean('Add separator',default=True)


		


