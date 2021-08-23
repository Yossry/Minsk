import pdb
import time
import math
import re

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


#from datetime import date
#from datetime import timedelta
#from dateutil import relativedelta

#from calendar import monthrange 

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

# Remarked by Farooq
#class AccountAssetAsset(models.Model):
#	_name = 'account.asset.asset'
#	_inherit = 'account.asset.asset'
#
#	center_id = fields.Many2one('sos.center', string='Center',required=True)
#	
#class asset_asset(models.Model):
#	_name = 'asset.asset'
#	_inherit = 'asset.asset'
#
#	@api.depends('category_id','center_id')
#	@api.one
#	def _get_asset_code(self):
#		#pdb.set_trace()
#		if self.category_id and self.center_id:
#			if not self.asset_number:
#				self.asset_number = self.env['ir.sequence'].next_by_code('asset.number')
#			code_pattern = '{categ}-{loc}-{acode}'
#			self.asset_code = code_pattern.format(categ=self.category_id.name, loc=self.center_id.code, acode=self.asset_number)
#
#	center_id = fields.Many2one('sos.center', string='Center',required=True)

# Remark by Numan
# class AccountReportGeneralLedger(models.TransientModel):
# 	_inherit = "account.common.account.report"
# 	_name = "account.report.general.ledger"
# 	_description = "General Ledger Report"

# 	initial_balance = fields.Boolean(string='Include Initial Balances', 
# 		help='If you selected date, this field allow you to add a row to display the amount of debit/credit	balance that precedes the filter you\'ve set.')
# 	sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
# 	journal_ids = fields.Many2many('account.journal', string='Journals', required=False, default=lambda self: self.env['account.journal'].search([('id','=',0)]))
# 	account_ids = fields.Many2many('account.account', string='Accounts')
	
# 	def _print_report(self, data):
# 		data = self.pre_print_report(data)
# 		data['form'].update(self.read(['initial_balance', 'sortby','account_ids'])[0])
# 		if data['form'].get('initial_balance') and not data['form'].get('date_from'):
# 			raise UserError(_("You must define a Start Date"))
# 		return self.env['report'].with_context(landscape=True).get_action(self, 'account.report_generalledger', data=data)

# class ReportGeneralLedger(models.AbstractModel):
# 	_name = 'report.account.report_generalledger'
# 	_inherit = 'report.account.report_generalledger'

# 	@api.multi
# 	def render_html(self, data):
# 		self.model = self.env.context.get('active_model')
# 		docs = self.env[self.model].browse(self.env.context.get('active_id'))

# 		init_balance = data['form'].get('initial_balance', True)
# 		sortby = data['form'].get('sortby', 'sort_date')
# 		display_account = data['form']['display_account']
# 		codes = []
# 		if data['form'].get('journal_ids', False):
# 			codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
		
# 		if data['form'].get('account_ids', False):
# 			accounts = self.env['account.account'].browse(data['form'].get('account_ids'))
# 		else:
# 			accounts = self.env['account.account'].search([])
# 		accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
# 		docargs = {
# 			'doc_ids': self.ids,
# 			'doc_model': self.model,
# 			'data': data['form'],
# 			'docs': docs,
# 			'time': time,
# 			'Accounts': accounts_res,
# 			'print_journal': codes,
# 		}
# 		return self.env['report'].render('account.report_generalledger', docargs)


class account_move(models.Model):
	_name = 'account.move'
	_inherit = 'account.move'

	post_id = fields.Many2one('sos.post',related='line_ids.post_id', string="Post", store=True)
	date = fields.Date("Financial Date",required=True, states={'posted': [('readonly', True)]}, index=True, default=fields.Date.context_today)
	entry_date = fields.Date("Entry Date",states={'posted': [('readonly', True)]}, index=True, default=fields.Date.context_today)

	@api.model
	def create(self, vals):
		if vals.get('date',False):
			date = vals.get('date')
			
		if not vals.get('entry_date',False):
			vals['entry_date'] = vals['date']
		move = super(account_move, self.with_context(check_move_validity=False)).create(vals)
		move.assert_balanced()
		move.date = date
		move.line_ids.write({'date':date,'entry_date':move.entry_date})
		return move
	

class account_move_line(models.Model):
	_name = 'account.move.line'
	_inherit = 'account.move.line'
	_order = "id desc"
	
	post_id = fields.Many2one('sos.post', 'Post', readonly=True)
	date = fields.Date(related='move_id.date', string='Financial Date', index=True, store=True, copy=False)
	entry_date = fields.Date(related='move_id.entry_date', string='Entry Date', index=True, store=True, copy=False)


class AccountJournal(models.Model):
	_name = "account.journal"
	_inherit = "account.journal"

	type = fields.Selection([('deduction', 'Deduction'),('sale', 'Sale'),('sale_refund','Sale Refund'), ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Checks'), ('general', 'General'), ('situation', 'Opening/Closing Situation')], 'Type', required=True, help="Select 'Sale' for customer invoices journals.\n" \
								 " Select 'Purchase' for supplier invoices journals.\n"\
								 " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments.\n"\
								 " Select 'General' for miscellaneous operations journals.\n"\
								 " Select 'Opening/Closing Situation' for entries generated for new fiscal years.")


class account_abstract_payment(models.AbstractModel):
	_name = "account.abstract.payment"
	_inherit = "account.abstract.payment"

	entry_date = fields.Date(string='Entry Date', default=fields.Date.context_today, required=True, copy=False)
	journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash','deduction'))])

	def _compute_journal_domain_and_types(self):
		journal_type = ['bank', 'cash','deduction']
		domain = []
		if self.currency_id.is_zero(self.amount) and self.has_invoices:
			# In case of payment with 0 amount, allow to select a journal of type 'general' like
			# 'Miscellaneous Operations' and set this journal by default.
			journal_type = ['general']
			self.payment_difference_handling = 'reconcile'
		else:
			if self.payment_type == 'inbound':
				domain.append(('at_least_one_inbound', '=', True))
			else:
				domain.append(('at_least_one_outbound', '=', True))
		return {'domain': domain, 'journal_types': set(journal_type)}


class account_register_payments(models.TransientModel):
	_name = "account.register.payments"
	_inherit = 'account.register.payments'

	entry_date = fields.Date(string='Entry Date', default=fields.Date.context_today, required=True, copy=False)


class account_payment(models.Model):
	_name = "account.payment"
	_inherit = 'account.payment'

	multi_partner = fields.Boolean("Multi Partner")
	multi_payment_id = fields.Many2one('account.multi.partner.payments',"Multi-Partner Payment")
	entry_date = fields.Date(string='Entry Date', default=fields.Date.context_today, required=True, copy=False)
	#journal_id = fields.Many2one('account.journal', string='Payment Method3', required=True,
	#							 domain=[('type', 'in', ('bank', 'cash', 'deduction'))])

	def _get_move_vals(self, journal=None):
		""" Return dict to create the payment move"""
		journal = journal or self.journal_id
		if not journal.sequence_id:
			raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
		if not journal.sequence_id.active:
			raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
		name = journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
		return {
			'name': name,
			'date': self.payment_date,
			'partner_id': self.partner_id.id,
			'entry_date': self.entry_date,
			'ref': self.communication or '',
			'company_id': self.company_id.id,
			'journal_id': journal.id,
		}

	@api.multi
	def multi_post(self):
		for rec in self:
			mgs = ""
			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
			if any(inv.state != 'open' for inv in rec.invoice_ids):
				op_invoices = self.env['account.invoice'].search([('state','!=','open'),('id','in',rec.invoice_ids.ids)])
				for op_invoice in op_invoices:
					mgs = mgs + '\n' + " Invoice : " + op_invoice.number + " \n State : " + op_invoice.state
				raise UserError(_('Following Invoices are not in the Open State. %s') % (mgs,))

			rec.name = rec.multi_payment_id.name
			# Create the journal entry
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
			move = rec._create_payment_entry(amount)
			rec.state = 'posted'	

	@api.onchange('payment_type')
	def _onchange_payment_type(self):
		if not self.invoice_ids:
			# Set default partner type for the payment type
			if self.payment_type == 'inbound':
				self.partner_type = 'customer'
			elif self.payment_type == 'outbound':
				self.partner_type = 'supplier'
		# Set payment method domain
		res = self._onchange_journal()
		if not res.get('domain', {}):
			res['domain'] = {}
		res['domain']['journal_id'] = self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or [('at_least_one_outbound', '=', True)]
		res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash','deduction')))		
		return res

		
class account_multi_partner_payments(models.Model):
	_name = "account.multi.partner.payments"
	_inherit = 'account.abstract.payment'
	_description = "Register payments on multiple Partner invoices"

	name = fields.Char(readonly=True, copy=False, default="Draft Payment")	
	state = fields.Selection([('draft','Draft'),('cancel','Cancelled'),('posted','Posted')],default='draft')
	multi_partner_payments_ids = fields.One2many('account.multi.partner.payments.line', 'multi_partner_payments_id', string='Payment Lines')

	@api.onchange('payment_type')
	def _onchange_payment_type(self):
		invoices = self._get_invoices()
		if invoices:
			payment_line_data = []
			for invoice in invoices:
				payment_line_data.append({
					'multi_partner_payments_id': self.id,
					'invoice_id': invoice.id,						
					'amount_original': invoice.residual,
					'amount_paid': 0,
					'amount_residual': invoice.residual,
				})
			payment_lines = self.multi_partner_payments_ids.browse([])
			for payment_line in payment_line_data:
				payment_lines += payment_lines.new(payment_line)
			self.multi_partner_payments_ids = payment_lines			

		if self.payment_type:
			return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

	def _get_invoices(self):
		active_model = self._context.get('active_model')
		active_ids = self._context.get('active_ids')
		if active_model and active_model == 'account.invoice' and active_ids: 		
			return self.env['account.invoice'].browse(self._context.get('active_ids'))
		return False
	
	@api.model
	def default_get(self, fields):
		rec = super(account_multi_partner_payments, self).default_get(fields)
		context = dict(self._context or {})
		active_model = context.get('active_model')
		active_ids = context.get('active_ids')
		total_amount = 0
		
		# Checks on received invoice records
		invoices = self._get_invoices()
		if invoices:
			if any(invoice.state != 'open' for invoice in invoices):
				raise UserError(_("You can only register payments for open invoices"))
			if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in invoices):
				raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
			if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
				raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

			total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
				
		rec.update({
			'amount': abs(total_amount),
			'currency_id': self.env.user.company_id.currency_id.id,
			'payment_type': 'inbound',
			'partner_id': 1,
			'partner_type': 'customer',		
		})
		return rec

	def get_payment_vals(self):
		""" Hook for extension """
		return {
			'journal_id': self.journal_id.id,
			'payment_method_id': self.payment_method_id.id,
			'payment_date': self.payment_date,
			'entry_date': self.entry_date,
			'communication': self.communication,
			'invoice_ids': False,
			'payment_type': self.payment_type,
			'amount': self.amount,
			'currency_id': self.currency_id.id,
			'partner_id': 1,
			'partner_type': self.partner_type,
		}

	@api.multi
	def create_payment(self):
		payments = self.multi_partner_payments_ids
		total_paid = sum(line.amount_paid for line in payments)
		if self.amount != total_paid:
			raise UserError(_("Total Paid amount and Invoices Paid Total Mismatch."))	
		payment_dict = self.get_payment_vals()
		sequence = self.env.ref('account.sequence_payment_multi_partner')
		self.name = sequence.with_context(ir_sequence_date=self.payment_date).next_by_id()
		
		##CASE(1)
		if not all([pyment.invoice_id for pyment in payments]):
			cnt = 0
			mgs = ''
			for pl in payments:
				if not pl.invoice_id:
					cnt +=1
					mgs = mgs + "\n "+ str(cnt) +":-"  +"\n Payment Line " + str(pl.id) + " does not have the Invoice Reference." + "\n Original Amount is :" + str(pl.amount_original) + " \n Amount Paid : " + str(pl.amount_paid)
			raise UserError(_("There are Lines in the Payment that do not have the Proper Data Formating \n or Missing Some Information, Detail is Below %s \n\n Solution:- \n Delete that Record from your Payment.\n There Should be Invoice Reference for each Line.") % (mgs,))		
		
		for line in payments:
			payment_dict.update({
				'invoice_ids':[(4, line.invoice_id.id, None)],
				'amount':line.amount_paid,
				'partner_id':line.invoice_id.partner_id.id,
				'multi_payment_id':self.id,
				'multi_partner':True,
			})
			
			#payment = self.env['account.payment'].with_context(mail_create_nosubscribe=True).create(payment_dict)
			payment = self.env['account.payment'].create(payment_dict)
			payment.multi_post()
		
		self.state='posted'
				
		return {'type': 'ir.actions.act_window_close'}


class account_multi_partner_payments_line(models.Model):
	_name = "account.multi.partner.payments.line"
	_description = 'Multi Partner Payment Lines'

	@api.one
	@api.depends('invoice_id','amount_paid')
	def _compute_balance(self):
		if self.invoice_id:
			self.amount_original = self.invoice_id.residual
			self.amount_residual = self.invoice_id.residual	- self.amount_paid		

	invoice_id = fields.Many2one('account.invoice','Invoice')
	reconcile = fields.Boolean('Full Reconcile')
	amount_original = fields.Integer(compute='_compute_balance', string='Original Amount', store=True)
	amount_paid = fields.Integer(string='Paid', default=0)
	amount_residual = fields.Integer(compute='_compute_balance', string='Residual Amount', store=True)
	multi_partner_payments_id = fields.Many2one('account.multi.partner.payments')
	post_id = fields.Many2one('sos.post', related='invoice_id.post_id',string='Partner')


class account_bank_statement(models.Model):
	_name = "account.bank.statement"
	_inherit = "account.bank.statement"
	
	entry_date = fields.Date(required=True, string="Entry Date",states={'confirm': [('readonly', True)]}, copy=False, default=fields.Date.context_today)
	combine_entries = fields.Boolean('Combine Journal Entries',default=True)
	combined_narration = fields.Text('Narration')
	
	@api.model
	def create(self, vals):
		if not vals.get('name',False):
			journal_id = vals.get('journal_id', self._context.get('default_journal_id', False))
			journal = self.env['account.journal'].browse(journal_id)
			vals['name'] = journal.sequence_id.with_context(ir_sequence_date=vals.get('date')).next_by_id()
		return super(account_bank_statement, self).create(vals)
	
	
#	def move_line_get_item(self, cr, uid, line, st_number, context=None):
#		return {
#			'type': 'src',
#			'name': line.name,
#			'date': line.date,
#			'ref': st_number,			
#			'partner_id': line.partner_id and line.partner_id.id or False,
#			'account_id': line.account_id.id,
#			'price': -line.amount,
#			'statement_id': line.statement_id.id,
#			'journal_id': line.statement_id.journal_id.id,
#			'period_id': line.statement_id.period_id.id,
#			'center_id': line.center_id.id,
#			#'currency_id': line.amount,
#			#'amount_currency': amount_currency,
#			
#			#'account_analytic_id': line.account_analytic_id.id,
#			'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
#			
#		}
#
#	def _get_analytic_lines(self, cr, uid, id, st_number,context=None):
#		iml = []
#		if context is None:
#			context = {}
#		st = self.browse(cr, uid, id)
#		cur_obj = self.pool.get('res.currency')
#
#		company_currency = self.pool['res.company'].browse(cr, uid, st.company_id.id).currency_id.id
#		sign = 1
#		total = 0
#		
#		for line in st.line_ids:
#			mres = self.move_line_get_item(cr, uid, line, st_number,context)
#			if not mres:
#				continue
#			iml.append(mres)
#			total += line.amount
#		
#		#for il in iml:
#		#	if il['account_analytic_id']:
#		#		if inv.type in ('in_invoice', 'in_refund'):
#		#			ref = inv.reference
#		#		else:
#		#			ref = self._convert_ref(cr, uid, inv.number)
#		#		if not inv.journal_id.analytic_journal_id:
#		#			raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
#		#		il['analytic_lines'] = [(0,0, {
#		#			'name': il['name'],
#		#			'date': inv['date_invoice'],
#		#			'account_id': il['account_analytic_id'],
#		#			'unit_amount': il['quantity'],
#		#			'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign,
#		#			'product_id': il['product_id'],
#		#			'product_uom_id': il['uos_id'],
#		#			'general_account_id': il['account_id'],
#		#			'journal_id': inv.journal_id.analytic_journal_id.id,
#		#			'ref': ref,
#		#		})]
#		return total, iml
#	
#	def compute_statement_totals(self, cr, uid, st, company_currency, ref, statement_move_lines, context=None):
#		if context is None:
#			context={}
#		total = 0
#		total_currency = 0
#		cur_obj = self.pool.get('res.currency')
#		for i in statement_move_lines:
#			i['amount_currency'] = False
#			i['currency_id'] = False
#			i['ref'] = ref
#			total += i['amount']
#			total_currency += i['amount_currency'] or i['amount']
#						
#		return total, total_currency, statement_move_lines
#
#	def line_get_convert(self, cr, uid, x, date, context=None):
#		
#		return {			
#			'partner_id': x.get('partner_id',False),
#			'name': x['name'],
#			'date': date,
#			'debit': x['price']>0 and x['price'],
#			'credit': x['price']<0 and -x['price'],
#			'account_id': x['account_id'],
#			'analytic_lines': x.get('analytic_lines', []),
#			'amount_currency': False,
#			'ref': x.get('ref', False),
#			'statement_id': x.get('statement_id', False),
#			'center_id': x.get('center_id', False),
#			'analytic_account_id': x.get('account_analytic_id', False),	
#		}
#
#
#	def button_confirm_bank(self, cr, uid, ids, context=None):
#		obj_seq = self.pool.get('ir.sequence')
#		move_obj = self.pool.get('account.move')
#		
#		if context is None:
#			context = {}
#
#		for st in self.browse(cr, uid, ids, context=context):
#			j_type = st.journal_id.type
#			company_currency_id = st.journal_id.company_id.currency_id.id
#			if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
#				continue
#
#			self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
#			if (not st.journal_id.default_credit_account_id) or (not st.journal_id.default_debit_account_id):
#				raise osv.except_osv(_('Configuration Error!'),_('Please verify that an account is defined in the journal.'))
#
#			if not st.name == '/':
#				st_number = st.name
#			else:
#				c = {'fiscalyear_id': st.period_id.fiscalyear_id.id}
#				if st.journal_id.sequence_id:
#					st_number = obj_seq.next_by_id(cr, uid, st.journal_id.sequence_id.id, context=c)
#				else:
#					st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)
#
#			for line in st.move_line_ids:
#				if line.state <> 'valid':
#					raise osv.except_osv(_('Error!'),('The account entries lines are not in valid state.'))
#			
#			
#			if st.combine_entries:
#						
#				cur_obj = self.pool.get('res.currency')
#				period_obj = self.pool.get('account.period')
#				journal_obj = self.pool.get('account.journal')				
#
#				if not st.line_ids:
#					raise osv.except_osv(_('No Statement Lines!'), _('Please create some statement lines.'))
#				#if st.move_id:
#				#	continue
#
#				ctx = context.copy()			
#
#				if not st.date:
#					self.write(cr, uid, [st.id], {'date': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
#						
#				company_currency = self.pool['res.company'].browse(cr, uid, st.company_id.id).currency_id.id
#				# create the analytical lines
#				# one move line per invoice line
#
#				total, iml = self._get_analytic_lines(cr, uid, st.id, st_number,context=ctx)
#
#				# create one move line for the total and possibly adjust the other lines amount
#									
#				acc_id = st.account_id.id
#				name = st['name'] or '/'
#
#				iml.append({
#					'type': 'dest',
#					'name': st.combined_narration,
#					'price': total,
#					'account_id': acc_id,
#					'amount_currency': False,
#					'currency_id': False,
#					'statement_id': st.id,
#					'ref': st_number
#				})
#
#				date = st.date or time.strftime('%Y-%m-%d')			
#				journal_id = st.journal_id.id
#
#				line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, date, context=ctx)),iml)
#
#				# Baad mein
#				#line = self.group_lines(cr, uid, iml, line, inv)
#			
#				move = {
#					'name': st_number,
#					'ref': self._convert_ref(cr, uid, st_number),
#					'line_ids': line,
#					'journal_id': journal_id,
#					'date': date,
#					'narration': st.combined_narration,
#					'company_id': st.company_id.id,
#				}
#				period_id = st.period_id and st.period_id.id or False
#				ctx.update(company_id=st.company_id.id,account_period_prefer_normal=True)
#				if not period_id:
#					period_ids = period_obj.find(cr, uid, st.date, context=ctx)
#					period_id = period_ids and period_ids[0] or False
#				if period_id:
#					move['period_id'] = period_id
#					for i in line:
#						i[2]['period_id'] = period_id
#
#				ctx.update(statement=st)
#
#						
#				move_id = move_obj.create(cr, uid, move, context=ctx)
#				new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
#				# make the statement point to that move
#				self.write(cr, uid, [st.id], {
#					'move_id': move_id,
#					'period_id':period_id,
#					'move_name':new_move_name
#				}, context=ctx)
#								
#								
#				# Pass invoice in context in method post: used if you want to get the same
#				# account move reference when creating the same invoice after a cancelled one:
#				#move_obj.post(cr, uid, [move_id], context=ctx)
#				#self._log_event(cr, uid, ids)	
#			
#			else:        
#				for st_line in st.line_ids:
#					if st_line.analytic_account_id:
#						if not st.journal_id.analytic_journal_id:
#							raise osv.except_osv(_('No Analytic Journal!'),_("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
#					if not st_line.amount:
#						continue
#					st_line_number = self.get_next_st_line_number(cr, uid, st_number, st_line, context)
#					self.create_move_from_st_line(cr, uid, st_line.id, company_currency_id, st_line_number, context)
#				
#			self.write(cr, uid, [st.id], {'name': st_number,'balance_end_real': st.balance_end}, context=context)
#			self.message_post(cr, uid, [st.id], body=_('Statement %s confirmed, journal items were created.') % (st_number,), context=context)
#		return self.write(cr, uid, ids, {'state':'confirm'}, context=context)


class account_bank_statement_line(models.Model):
	_name = "account.bank.statement.line"
	_inherit = "account.bank.statement.line"

	center_id = fields.Many2one('sos.center', 'Center',default=19)	
	entry_date = fields.Date(required=True, string="Entry Date",default=lambda self: self._context.get('date', fields.Date.context_today(self)))

	
#class purchase_order(osv.osv):
#	_name = "purchase.order"
#	_inherit = "purchase.order" 
#	
#	def _choose_account_from_po_line(self, cr, uid, po_line, context=None):
#		fiscal_obj = self.pool.get('account.fiscal.position')
#		property_obj = self.pool.get('ir.property')
#		if po_line.product_id:
#			
#			acc_id = po_line.product_id.categ_id.property_stock_account_input_categ.id
#			if not acc_id:
#				acc_id = po_line.product_id.property_account_expense.id
#			if not acc_id:
#				acc_id = po_line.product_id.categ_id.property_account_expense_categ.id
#			if not acc_id:
#				raise osv.except_osv(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (po_line.product_id.name, po_line.product_id.id,))
#		else:
#			acc_id = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category', context=context).id
#		fpos = po_line.order_id.fiscal_position or False
#		return fiscal_obj.map_account(cr, uid, fpos, acc_id)
#		
#class account_voucher(osv.osv):
#	_name = "account.voucher"
#	_inherit = "account.voucher" 
#
#	def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
#		if context is None:
#			context = {}
#		if not journal_id:
#			return False
#		journal_pool = self.pool.get('account.journal')
#		journal = journal_pool.browse(cr, uid, journal_id, context=context)
#		account_id = journal.default_credit_account_id or journal.default_debit_account_id
#		tax_id = False
#		if account_id and account_id.tax_ids:
#			tax_id = account_id.tax_ids[0].id
#	
#		vals = {'value':{} }
#		if ttype in ('sale', 'purchase'):
#			vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
#			vals['value'].update({'tax_id':tax_id,'amount': amount})
#		currency_id = False
#		if journal.currency:
#			currency_id = journal.currency.id
#		else:
#			currency_id = journal.company_id.currency_id.id
#
#		vals['value'].update({
#			'currency_id': currency_id,
#			'payment_rate_currency_id': currency_id,
#		
#		})
#	        
#		if partner_id:
#			res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
#			for key in res.keys():
#				vals[key].update(res[key])
#		return vals


class Followers(models.Model):
	_inherit = 'mail.followers'

	_sql_constraints = [
		('mail_followers_res_partner_res_model_id_uniq', 'unique(id,res_model,res_id,partner_id)', 'Error, a partner cannot follow twice the same object.'),
		('mail_followers_res_channel_res_model_id_uniq', 'unique(id,res_model,res_id,channel_id)', 'Error, a channel cannot follow twice the same object.'),
	]
