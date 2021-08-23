import time
import pdb
from itertools import groupby
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _

from odoo.tools import config
from odoo.addons.analytic_structure.MetaAnalytic import MetaAnalytic
import math


#class account_payment(models.Model):
#	_inherit = 'account.payment'

#	def _get_counterpart_move_line_vals(self, invoice=False):
#		move_line = super(account_payment, self)._get_counterpart_move_line_vals(invoice)
#		move_line['payment_id'] = self.id
		
#		model_rec = self.env['ir.model'].search([('model','=','account.payment')])
#		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')
			
#		number = 0
#		nd_ids = self.destination_account_id.nd_ids
#		if nd_ids:
#			for auto_entry in auto_entries:
#				if auto_entry.dimension_id in nd_ids:
#					#Only for Dokkan Afkar
#					#if not self.shipper_id:
#					#	self.shipper_id = self.order_id.carrier_id and self.order_id.carrier_id.id
#					
#					move_line.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
#					ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
#					number += math.pow(2,int(ans.ordering)-1)			
#			move_line.update({'d_bin' : bin(int(number))[2:].zfill(10)})
#	
#		return move_line
#
#class account_payment_line(models.Model, metaclass = MetaAnalytic):
#	_inherit = "account.payment.line"
#	_analytic = True


class account_payment(models.Model):
	_name = "account.payment"
	_inherit = 'account.payment'

	oldref2 = fields.Char()
	old_ref = fields.Char()
	
	user_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	payment_type = fields.Selection([('outbound', 'Vendor Payment'), ('inbound', 'Customer Receipt'),('transfer', 'Internal Transfer'),
		('outbound_g', 'General Payment'), ('inbound_g', 'General Receipt')], string='Payment Type', required=True)
		
	user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
	payment_lines = fields.One2many('account.payment.line', 'payment_id',string='Payment Lines')

	def _get_counterpart_move_line_vals(self, invoice=False):
		model_rec = self.env['ir.model'].search([('model','=','account.payment')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')

		if self.payment_type == 'transfer':
			name = self.name
		else:
			name = ''
			if self.partner_type == 'customer':
				if self.payment_type == 'inbound':
					name += _("Customer Payment")
				elif self.payment_type == 'outbound':
					name += _("Customer Refund")
			elif self.partner_type == 'supplier':
				if self.payment_type == 'inbound':
					name += _("Vendor Refund")
				elif self.payment_type == 'outbound':
					name += _("Vendor Payment")
			if invoice:
				name += ': '
				for inv in invoice:
					if inv.move_id:
						name += inv.number + ', '
				name = name[:len(name)-2] 
				
		move_line = {
			'name': name,
			'account_id': self.destination_account_id.id,
			'journal_id': self.journal_id.id,
			'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
			'payment_id': self.id,
			'partner_id' : (self.partner_id and self.partner_id.id) or (invoice and invoice.partner_id.id) or False,
		}
		
		number = 0
		nd_ids = self.destination_account_id.nd_ids
		if nd_ids:
			for auto_entry in auto_entries:
				if auto_entry.dimension_id in nd_ids:
					move_line.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
					ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
					number += math.pow(2,int(ans.ordering)-1)			
			move_line.update({'d_bin' : bin(int(number))[2:].zfill(10)})
		return move_line

	def _get_liquidity_move_line_vals(self, amount):
		model_rec = self.env['ir.model'].search([('model','=','account.payment')])
		auto_entries = self.env['auto.dimensions.entry'].search([('model_id','=',model_rec.id),('active','=',True)],order='sequence')

		name = self.name
		if self.payment_type == 'transfer':
			name = _('Transfer to %s') % self.destination_journal_id.name
		vals = {
			'name': name,
			'account_id': self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
			'journal_id': self.journal_id.id,
			'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
		}
		
		account = self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id or self.journal_id.default_credit_account_id

		# If the journal has a currency specified, the journal item need to be expressed in this currency
		if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
			amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
			debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
			vals.update({
				'amount_currency': amount_currency,
				'currency_id': self.journal_id.currency_id.id,
			})
			
		
		number = 0
		nd_ids = account.nd_ids
		if nd_ids:
			for auto_entry in auto_entries:
				if auto_entry.dimension_id in nd_ids:
					vals.update({auto_entry.dst_col.name : eval(auto_entry.src_fnc)})
					ans = self.env['analytic.structure'].search([('model_name','=','account_move_line'),('nd_id','=',auto_entry.dimension_id.id)])	
					number += math.pow(2,int(ans.ordering)-1)			
			vals.update({'d_bin' : bin(int(number))[2:].zfill(10)})
		return vals

	@api.multi
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconciliable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		
		for rec in self:
			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

			if any(inv.state != 'open' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

			# Use the right sequence to set the name
			if rec.payment_type == 'transfer':
				sequence_code = 'account.payment.transfer'
			else:
				if rec.partner_type == 'customer':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.customer.invoice'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.customer.refund'
				if rec.partner_type == 'supplier':
					if rec.payment_type == 'inbound':
						sequence_code = 'account.payment.supplier.refund'
					if rec.payment_type == 'outbound':
						sequence_code = 'account.payment.supplier.invoice'
			
			rec.name = rec.oldref2 or self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
			# Create the journal entry
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
			move = rec._create_payment_entry(amount)

			# In case of a transfer, the first journal entry created debited the source liquidity account and credited
			# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
			if rec.payment_type == 'transfer':
				transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
				transfer_debit_aml = rec._create_transfer_entry(amount)
				(transfer_credit_aml + transfer_debit_aml).reconcile()

			rec.state = 'posted'

	def _get_move_vals(self, journal=None):
		""" Return dict to create the payment move
		"""
		journal = journal or self.journal_id
		if not journal.sequence_id:
			raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
		if not journal.sequence_id.active:
			raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

		name = self.name		
		#name = journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
		return {
			'name': name,
			'date': self.payment_date,
			'ref': self.communication or '',
			'company_id': self.company_id.id,
			'journal_id': journal.id,
		}


class account_payment_line(models.Model,metaclass = MetaAnalytic):
	_name = "account.payment.line"
	_analytic = True

	@api.model
	def _get_currency(self):
		currency = False
		context = self._context or {}
		if context.get('default_journal_id', False):
			currency = self.env['account.journal'].browse(context['default_journal_id']).currency_id
		return currency

	name = fields.Char(required=True, string="Label")
	amount = fields.Monetary(default=0.0, currency_field='company_currency_id')
	amount_currency = fields.Monetary(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,help='Utility field to express amount currency', store=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=_get_currency, help="The optional other currency if it is a multi-currency entry.")
	account_id = fields.Many2one('account.account', string='Account', required=True, index=True, ondelete="cascade", domain=[('deprecated', '=', False)], 
		default=lambda self: self._context.get('account_id', False))
	move_id = fields.Many2one('account.move', string='Journal Entry', ondelete="cascade", help="The move of this entry line.", index=True, required=True, auto_join=True)
	narration = fields.Text(related='move_id.narration', string='Internal Note')
	ref = fields.Char(related='move_id.ref', string='Partner Reference', store=True, copy=False)
	payment_id = fields.Many2one('account.payment', string="Originator Payment", help="Payment that created this entry")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	old_ref = fields.Char()

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
	#partner_code = fields.Char(related='account_id.partner_code')

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