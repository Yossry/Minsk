import pdb
import math
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo.tools import float_is_zero
import itertools
from odoo import netsvc
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import Warning, RedirectWarning,UserError
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp
#from odoo.tools.amount_to_text_en import english_number

import logging
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
	_name = "account.invoice"
	_inherit = "account.invoice"
	_description = "SOS Invoice"
	_order = "number desc, id desc"
	
	## Over Method For Rounding ##
	@api.one
	@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id')
	def _compute_amount(self):
		self.amount_untaxed = round(sum(line.price_subtotal for line in self.invoice_line_ids))
		self.amount_tax = round(sum(line.amount for line in self.tax_line_ids))
		self.amount_total = round(self.amount_untaxed + self.amount_tax)
		amount_total_company_signed = round(self.amount_total)
		amount_untaxed_signed = round(self.amount_untaxed)
		if self.currency_id and self.currency_id != self.company_id.currency_id:
			amount_total_company_signed = round(self.currency_id.compute(self.amount_total, self.company_id.currency_id))
			amount_untaxed_signed = round(self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id))
		sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		self.amount_total_company_signed = round(amount_total_company_signed * sign)
		self.amount_total_signed = round(self.amount_total * sign)
		self.amount_untaxed_signed = round(amount_untaxed_signed * sign)
	
	## Over Method For Rounding ##
	@api.one
	@api.depends(
		'state', 'currency_id', 'invoice_line_ids.price_subtotal',
		'move_id.line_ids.amount_residual',
		'move_id.line_ids.currency_id')
	def _compute_residual(self):
		residual = 0.0
		residual_company_signed = 0.0
		sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		for line in self.sudo().move_id.line_ids:
			if line.account_id.internal_type in ('receivable', 'payable'):
				residual_company_signed += line.amount_residual
				if line.currency_id == self.currency_id:
					residual += line.amount_residual_currency if line.currency_id else line.amount_residual
				else:
					from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
					residual += from_currency.compute(line.amount_residual, self.currency_id)
		residual = round(residual)			
		self.residual_company_signed = abs(residual_company_signed) * sign
		self.residual_signed = abs(residual) * sign
		self.residual = abs(residual)
		digits_rounding_precision = self.currency_id.rounding
		if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
			self.reconciled = True
		else:
			self.reconciled = False
	
	@api.one	
	def _check_duration(self):
		return self.date_to < self.date_from
	state = fields.Selection([
		('draft','Draft'),
		('proforma', 'Pro-forma'),
		('proforma2', 'Pro-forma'),
		('checked', 'Checked'),
		('open', 'Approved'),
		('paid', 'Paid'),
		('cancel', 'Cancelled'),
		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False,
		help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
			" * The 'Pro-forma' status is used the invoice does not have an invoice number.\n"
			" * The 'Open' status is used when user create invoice, an invoice number is generated. Its in open status till user does not pay invoice.\n"
			" * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
			" * The 'Cancelled' status is used when user cancel invoice.")

	invoice_type = fields.Selection([('days','Days'),('hours','Hours'),],'Invoice Service', change_default=True, track_visibility='onchange', default='days')	
	inv_type = fields.Selection([('regular','Regular'),('debit','Debit Note'),('credit','Credit Note')],'Invoice Type', change_default=True, track_visibility='onchange', default='regular')	
	
	period_id = fields.Many2one('sos.period','Period')
	checked_by = fields.Many2one('res.users', 'Checked By', readonly=True, track_visibility='onchange', states={'checked':[('readonly',False)]})
	approved_by = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange', states={'open':[('readonly',False)]})
	post_id = fields.Many2one('sos.post', string='Post', change_default=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='always')
		
	for_month = fields.Char('Invoice Month', size=32, readonly=True, states={'draft':[('readonly',False)]}, track_visibility='onchange')
	project_id = fields.Many2one('sos.project', related='post_id.project_id', readonly=True, store=True, string='Project',track_visibility='always')
	center_id = fields.Many2one('sos.center', related='post_id.center_id', readonly=True, store=True, string='Center',track_visibility='always')		

	date_from = fields.Date('From Date', readonly=True, states={'draft':[('readonly',False)]}, default=lambda self: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date('To Date', readonly=True, states={'draft':[('readonly',False)]},default=lambda self: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])
	parent_id = fields.Many2one('account.invoice','Parent Invoice',readonly=True,states={'draft': [('readonly', False)]}, help='This is the main invoice that has generated this credit note')
	
	part_id = fields.Integer(string='Partner (Dummy)', readonly=True, states={'draft': [('readonly', False)]})
	res_id = fields.Integer(string='ID (Dummy)')
	to_be_processed = fields.Boolean('To Be Processed',default=False)
	
	p_total = fields.Integer("Payment Total")
	pm_total = fields.Integer("Payment Move Total")
	finalized = fields.Boolean("Finalized")
	incentive = fields.Boolean("Incentive Invoice")

	_constraints = [
		(_check_duration, _('Error! The Time Period of Invoice is invalid.'), ['date_from','date_to']),
	]

	@api.onchange('post_id')
	def _onchange_post_id(self):
		if self.post_id:
			self.partner_id = self.post_id.partner_id

	@api.multi
	def _track_subtype(self, init_values):
		self.ensure_one()
		if 'state' in init_values and self.state == 'checked' and self.type in ('out_invoice', 'out_refund'):
			return 'account.mt_invoice_checked'
		return super(account_invoice, self)._track_subtype(init_values)

	@api.model
	def recompute_payments(self,nlimit=100):
		invoices = self.search([('to_be_processed','=',True)],limit=nlimit)	
		for invoice in invoices:	
			
			p_total = 0
			pm_total = 0
			line_obj = self.env['account.move.line']
			reconcile_obj = self.env['account.partial.reconcile']

			invoice._compute_payments()
			residual = 0.0
			residual_company_signed = 0.0
			total = 0.0
			total_company_signed = 0.0
			sign = invoice.type in ['in_refund', 'out_refund'] and -1 or 1
			
			for line in invoice.sudo().move_id.line_ids:
				if line.account_id.internal_type in ('receivable', 'payable'):
					total += line.debit
					concile_ids = reconcile_obj.search([('debit_move_id','=',line.id)])
					for concile in concile_ids:
						total -= concile.credit_move_id.credit
						
						concile.credit_move_id.amount_residual = 0
						concile.credit_move_id.amount_residual_currency = 0
						concile.credit_move_id.reconciled = True
						concile.credit_move_id.invoice_id = invoice.id

					_logger.warning('Changing Residual Value of Invoice %s ', (invoice.id))
					_logger.warning('Changing Residual Value of Move Line %s ', (line.id))

					line.amount_residual_currency = abs(total) * sign
					line.amount_residual = abs(total) * sign
					digits_rounding_precision = self.currency_id.rounding
					if float_is_zero(line.amount_residual, digits_rounding_precision):
						line.reconciled = True
			invoice._compute_residual()
			
			for line in invoice.payment_move_line_ids:
				pm_total += (line.debit - line.credit)
			for line in invoice.payment_ids:
				p_total += line.amount			
			invoice.p_total = p_total
			invoice.pm_total = pm_total			
			invoice.to_be_processed = False

	@api.multi
	def test_recompute(self):		
		for invoice in self:		
			p_total = 0
			pm_total = 0
			line_obj = self.env['account.move.line']
			reconcile_obj = self.env['account.partial.reconcile']

			invoice._compute_payments()
			residual = 0.0
			residual_company_signed = 0.0
			total = 0.0
			total_company_signed = 0.0
			sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
			
			for line in self.sudo().move_id.line_ids:
				if line.account_id.internal_type in ('receivable', 'payable'):
					total += line.debit
					concile_ids = reconcile_obj.search([('debit_move_id','=',line.id)])
					for concile in concile_ids:
						total -= concile.credit_move_id.credit
						
						concile.credit_move_id.amount_residual = 0
						concile.credit_move_id.amount_residual_currency = 0
						concile.credit_move_id.reconciled = True
						concile.credit_move_id.invoice_id = invoice.id
			
					line.amount_residual_currency = abs(total) * sign
					line.amount_residual = abs(total) * sign
					digits_rounding_precision = self.currency_id.rounding
					if float_is_zero(line.amount_residual, digits_rounding_precision):
						line.reconciled = True
			invoice._compute_residual()
			
			for line in invoice.payment_move_line_ids:
				p_total += (line.debit - line.credit)
			for line in invoice.payment_ids:
				pm_total += line.amount			
			invoice.p_total = p_total
			invoice.pm_total = pm_total			
			invoice.to_be_processed = False

	@api.onchange('partner_id', 'date_from','date_to')
	def _onchange_partner_id(self):
		super(account_invoice, self)._onchange_partner_id()		
		p = self.partner_id
		type = self.type
		incentive = self.incentive

		if not self.post_id:
			self.post_id = self.partner_id.post_id.id
			self.project_id = self.partner_id.post_id.project_id.id
			self.center_id = self.partner_id.post_id.center_id.id
		
		# add own logic
		if type in ('out_invoice', 'out_refund') and incentive == False:		
			invoice_line_vals = []
			tax_line_vals = []
			month_days = 31.00
			for_month = ''
			
			if p:
				partner_id = p.id
				post = self.env['sos.post'].search([('partner_id', '=', partner_id)])
				guard_recs = self.env['sos.post.jobs'].search([('post_id', '=', post.id)])
				ds = self.date_from
				dt = self.date_to
				month_days = ((dt-ds).days)+1
				for_month = dt.strftime('%B-%Y')

				for guard_rec in guard_recs:					
					ratepday = 1.00*guard_rec.rate/month_days									
					#account = self.env['account.invoice.line'].get_invoice_line_account(self.type,guard_rec.product_id,self.fiscal_position_id,self.company_id)
					insurance = self.env['account.tax'].search([('amount_type','=','insurance')])

					invoice_line_vals.append({
						'product_id': guard_rec.product_id,
						'invoice_id': self.id,						
						'name': guard_rec.product_id.partner_ref,
						#'account_id': account and account.id or False,
						'account_id' : self.journal_id.default_credit_account_id.id,
						'guardrate': guard_rec.rate,
						'guards': guard_rec.guards,
						'quantity': guard_rec.guards*month_days,
						'month_days': month_days,
						'price_unit': ratepday,
						'invoice_line_tax_ids': guard_rec.post_id.taxrate_id,
			
					})
				
				invoice_lines = self.invoice_line_ids.browse([])
				for invoice_line in invoice_line_vals:
					invoice_lines += invoice_lines.new(invoice_line)
				self.invoice_line_ids = invoice_lines
				
				account_id = 48	# Receivable
				
				self.account_id = account_id
				self.for_month = for_month
				self.date_invoice = datetime.today().strftime('%Y-%m-%d')
				self.date_due = str(datetime.now() + relativedelta.relativedelta(day=31))[:10]

	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line_ids(self):
		taxes_grouped = self.get_taxes_values()
		if self.type == 'out_invoice' and self.post_id.insurance:
			no_guards = 0
			for line in self.invoice_line_ids:
				no_guards = no_guards + line.guards

			taxes_grouped[999]={
				'invoice_id': self.id,
				'name': 'Insurance Claim P/S.G Rs. %s'%self.post_id.insurance,
				'account_id' : 146,  # Insurance Claim
				
				'amount': int(self.post_id.insurance) * no_guards,
				'manual' : 10,
			}		
		tax_lines = self.tax_line_ids.browse([])
		for tax in taxes_grouped.values():
			tax_lines += tax_lines.new(tax)
		self.tax_line_ids = tax_lines
		return		

	@api.model
	def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
		values = super(account_invoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
		#if invoice['type'] == 'in_invoice':
		for field in ['post_id', 'project_id', 'center_id', 'for_month', 'period_id','date_from','date_to']:
			if invoice._fields[field].type == 'many2one':
				values[field] = invoice[field].id
			else:
				values[field] = invoice[field] or False
		values['parent_id'] = invoice.id
		return values

	@api.multi
	def invoice_check(self):
		for rec in self:
			if rec.state == 'draft':
				rec.write({'state' :'checked','checked_by' : self.env.user.id})
	
	@api.multi
	def invoice_draft(self):
		for invoice in self:
			invoice.write({'state': 'draft'})	

	@api.multi
	def invoice_validate(self):
		result = super(account_invoice, self).invoice_validate()
		
		for invoice in self:
			if invoice.type == 'out_refund' and invoice.parent_id:        	
				movelines = invoice.parent_id.move_id.line_ids
				to_reconcile_ids = {}
				to_reconcile_lines = self.env['account.move.line']
				for line in movelines:
					if line.account_id.id == invoice.parent_id.account_id.id:
						to_reconcile_lines += line
						to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
					if line.reconciled:
						line.remove_move_reconcile()

				for tmpline in invoice.move_id.line_ids:
					if tmpline.account_id.id == invoice.account_id.id:
						to_reconcile_lines += tmpline
						
						to_reconcile_lines.reconcile()
		return result

#	@api.model
#	def line_get_convert(self, line, part, date):
#				
#		return {
#			'date_maturity': line.get('date_maturity', False),
#			'post_id': part,
#			'name': line['name'],
#			'date': date,
#			'debit': line['price']>0 and line['price'],
#			'credit': line['price']<0 and -line['price'],
#			'account_id': line['account_id'],
#			'analytic_lines': line.get('analytic_lines', []),
#			'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
#			'currency_id': line.get('currency_id', False),
#			'tax_code_id': line.get('tax_code_id', False),
#			'tax_amount': line.get('tax_amount', False),
#			'ref': line.get('ref', False),
#			'quantity': line.get('quantity',1.00),
#			'product_id': line.get('product_id', False),
#			'product_uom_id': line.get('uos_id', False),
#			'analytic_account_id': line.get('account_analytic_id', False),
#			'sos_invoice_id': line.get('sos_invoice_id', False),
#			'project_id': line.get('project_id', False),
#			'center_id': line.get('center_id', False),	
#		}


	@api.multi
	def finalize_invoice_move_lines(self, move_lines):
		move_lines = super(account_invoice, self).finalize_invoice_move_lines(move_lines)
		for move_line in move_lines:			
			if move_line[2]['name'] == '/' and self.for_month:
				move_line[2]['name'] = 'Invoice for ' + self.for_month
		return move_lines

	@api.multi
	@api.returns('self')
	def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
		new_invoices = self.browse()
		for invoice in self:
			# create the new invoice
			values = self._prepare_refund(invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
			values.update({'inv_type':'credit'})
			new_invoices += self.create(values)
		return new_invoices
	
	def amount_in_word(self, amount_total):
		number = '%.2f' % amount_total
		number = round(amount_total)
		units_name = 'PKR'
		lst = str(number).split('.')
		#start_word = english_number(int(list[0]))
		start_word =  self.currency_id.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(int(lst[0])).upper()
		return ' '.join(filter(None, [start_word, units_name]))

	@api.multi
	def action_invoice_open(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
		if to_open_invoices.filtered(lambda inv: inv.state != 'checked' and inv.type !='in_invoice'):
			raise UserError(_("Invoice must be in draft state in order to validate it."))
		if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
			raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))

		to_open_invoices.action_date_assign()
		to_open_invoices.action_move_create()
		return to_open_invoices.invoice_validate()
		
class account_invoice_line(models.Model):
	_name = "account.invoice.line"
	_inherit = "account.invoice.line"
	
	@api.one
	@api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
		'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
	def _compute_price(self):
		currency = self.invoice_id and self.invoice_id.currency_id or None
		price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
		taxes = False
		if self.invoice_line_tax_ids:
			taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
		self.price_subtotal = price_subtotal_signed = round(taxes['total_excluded'] if taxes else self.quantity * price)
		if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
			price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
		sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
		self.price_subtotal_signed = price_subtotal_signed * sign

	orig_invoice_id = fields.Integer(string='Invoice Ref.')
	post_id = fields.Many2one('sos.post', string='Partner Ref.', related='invoice_id.post_id', store=True, readonly=True)
	guards = fields.Integer(string='Guards', default=1, digits=dp.get_precision('Product'))
	month_days = fields.Integer(string='Days', digits=dp.get_precision('Product'))
	guardrate = fields.Float(string='Rate P/G', digits=dp.get_precision('Product')) 

#	@api.model
#	def move_line_get_item(self, line):
#		return {
#			'type': 'src',
#			'name': line.name,
#			'price_unit': line.price_unit,
#			'quantity': line.quantity,
#			'price': line.price_subtotal,
#			'account_id': line.account_id.id,
#			'product_id': line.product_id.id,
#			'uos_id': line.uos_id.id,
#			'account_analytic_id': line.account_analytic_id.id,
#			'taxes': line.invoice_line_tax_id,
#		}

	@api.onchange('guardrate')
	def _onchange_guardrate(self):
		for_month = self.invoice_id.date_invoice or False
		if not self.guardrate:
			return

		if self.invoice_id.date_from and self.invoice_id.date_to:
			ds = self.invoice_id.date_from
			dt = self.invoice_id.date_to
			month_days = (dt-ds).days + 1
		else:
			year,month,day = for_month[:4], for_month[5:7], for_month[8:]
			month_days = monthrange(int(year),int(month))[1]
			
		ratepday = self.guardrate/month_days        
		self.price_unit = ratepday

#	
#	@api.model
#	def move_line_get(self, invoice_id):
#		inv = self.env['sos.invoice'].browse(invoice_id)
#		currency = inv.currency_id.with_context(date=inv.date_invoice)
#		
#		res = []
#		for line in inv.invoice_line:
#			mres = self.move_line_get_item(line)
#			mres['invl_id'] = line.id
#			res.append(mres)
#			tax_code_found = False
#			taxes = line.invoice_line_tax_id.compute_all(line.price_unit, line.quantity, line.product_id, inv.post_id)['taxes']
#			for tax in taxes:
#				tax_code_id = tax['base_code_id']
#				tax_amount = line.price_subtotal * tax['base_sign']
#				
#				if tax_code_found:
#					if not tax_code_id:
#						continue
#					res.append(dict(mres))
#					res[-1]['price'] = 0.0
#					res[-1]['account_analytic_id'] = False
#				elif not tax_code_id:
#					continue
#				tax_code_found = True
#
#				res[-1]['tax_code_id'] = tax_code_id
#				res[-1]['tax_amount'] = tax_amount #currency.compute(tax_amount, company_currency)
#
#		return res


class sos_post(models.Model):
	_inherit = 'sos.post'

	@api.one
	@api.depends('invoice_ids')	
	def _invoices_count(self):		
		Invoice = self.env['account.invoice']
		self.invoices_count = Invoice.search_count([('post_id', '=', self.id)])
	
	@api.depends('invoice_ids.residual')	
	def _aged_balance(self):		
		Invoice = self.env['account.invoice']
		start_date = datetime.strptime('2014-07-01', "%Y-%m-%d").date()
		today = datetime.today().strftime('%Y-%m-%d')
		invoices = Invoice.search([('post_id', '=', self.id),('type', '=', 'out_invoice'),('date_due', '>=', start_date),('date_due','<=', today)])
		total = 0
		
		for invoice in invoices:
			total = total + invoice.residual
		self.aged_balance = round(total)
	
	invoice_ids = fields.One2many('account.invoice', 'post_id', string='Invoices', readonly=True)
	invoices_count = fields.Integer('Invoices Count',compute='_invoices_count')
	aged_balance = fields.Float('Aged Balance',compute='_aged_balance')
	


