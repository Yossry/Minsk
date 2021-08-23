import pdb
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models, _


class InvoicesDebitNoteWizard(models.TransientModel):
	_name = 'invoices.debit.note.wizard'
	_description = "Generate Invoices Debit Note Entries"
	
	@api.multi
	@api.depends('debit_line_ids')
	def _get_amount(self):
		for rec in self:
			total= 0 
			for line in rec.debit_line_ids:
				total = total +  line.invoice_total or 0
			rec.total = total	
	
	name = fields.Char("Name")
	date_from = fields.Date("Date From", default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	date_to = fields.Date("Date To", default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=31))[:10])
	due_date = fields.Date("Due Date")
	for_month = fields.Char('Invoice Month', size=32)
	debit_line_ids = fields.One2many("invoices.debit.note.lines.wizard", "debit_id", "Lines")
	total = fields.Float("Total Amount", compute="_get_amount")
	
	@api.one
	def generate_debit_entries(self):
		invoice_pool = self.env['account.invoice']
		invoice_ids = self.env['account.invoice']
		tax_obj = self.env['account.tax']
		
		for line in self.debit_line_ids:
			invoice_line_vals = []
			month_days = 31.00
			for_month = ''
			
			partner_id = line.post_id.partner_id.id
			post = self.env['sos.post'].search([('partner_id', '=', partner_id)])
			ds = self.date_from
			dt = self.date_to
			month_days = (dt-ds).days +1
			for_month = dt.strftime('%B-%Y')
			
			res = {
				'name' : 'Debit Note of ' + post.name + ' of ' + for_month,
				'type': 'out_invoice',
				'inv_type' : 'debit',
				'company_id': 1,
				'account_id': 48,  # Receivable
				'payment_term_id': False,
				'fiscal_position_id': False,
				'partner_id': line.post_id.partner_id.id,
				'post_id': line.post_id.id,
				'project_id': line.post_id.project_id.id,
				'center_id': line.post_id.center_id.id,
				'for_month': for_month,
				'date_invoice': dt or fields.Date.today(),
				'date_due':  self.due_date or str(datetime.now() + relativedelta.relativedelta(day=31))[:10],
				'date_from': ds,
				'date_to': dt,
				}
				
			invoice = invoice_pool.create(res)
			taxes_grouped = invoice.get_taxes_values()
			tax_grouped = {}
			invoice_line_vals.append({
				'invoice_id': invoice.id,
				'name': 'Debit Note of ' + post.name + ' of ' + for_month,					
				'account_id' : 94,   # Sales
				'month_days': month_days,
				'price_unit':line.invoice_total,
				})
				
			product_id = False
			quantity = 31
			ratepday = round(line.invoice_amount / quantity ) or 0 	
			taxes = line.post_id.taxrate_id.compute_all(ratepday, invoice.currency_id, quantity, product_id, invoice.partner_id)['taxes']
			for tax in taxes:
				val = {
					'invoice_id': invoice.id,
					'name': tax['name'],
					'tax_id': tax['id'],
					'amount': round(tax['amount']),
					'manual': False,
					'sequence': tax['sequence'],
					'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
					'account_id': invoice.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or 147) or (tax['refund_account_id'] or 147),   # General Sales Tax Payable 
				}                
				key = tax['id']
				if key not in tax_grouped:
					tax_grouped[key] = val
				else:
				    tax_grouped[key]['amount'] += val['amount']
			invoice_lines = invoice.invoice_line_ids.browse([])
			for invoice_line in invoice_line_vals:
				invoice_lines += invoice_lines.new(invoice_line)
			tax_lines = invoice.tax_line_ids.browse([])
			for tax in tax_grouped.values():
				tax_lines += tax_lines.new(tax)
			invoice.tax_line_ids = tax_lines
			invoice.invoice_line_ids = invoice_lines


class InvoicesDebitNoteLinesWizard(models.TransientModel):
	_name = 'invoices.debit.note.lines.wizard'
	_description = "Generate Invoices Debit Note Entry Lines"

	@api.multi
	@api.depends('invoice_amount','tax_amount')
	def _get_total_amount(self):
		for rec in self:
			rec.invoice_total = rec.invoice_amount + rec.tax_amount or 0
	
	#post_id = fields.Many2one('sos.post', string="Post", domain=[('project_id','in',[22,24,35])])
	post_id = fields.Many2one('sos.post', string="Post")
	invoice_amount = fields.Float("Invoice Amount")
	tax_amount = fields.Float("Tax Amount")
	invoice_total = fields.Float("Total",compute='_get_total_amount',store=True)
	debit_id = fields.Many2one("invoices.debit.note.wizard","Debit Note")
	
