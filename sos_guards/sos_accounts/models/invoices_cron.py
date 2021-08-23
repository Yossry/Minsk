from calendar import isleap
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import api, fields, models
from odoo import tools
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.tools.safe_eval import safe_eval as eval
DATETIME_FORMAT = "%Y-%m-%d"

class invoices_cron(models.Model):
	_name = 'invoices.cron'
	_description = 'Invoices Cron Jobs'
	_order = 'id desc'
		
	post_id = fields.Many2one('sos.post','Post')
	center_id = fields.Many2one('sos.center','Center')
	project_id = fields.Many2one('sos.project','Project')	
	date_from = fields.Date("Date From")
	date_to = fields.Date("Date To")
	state = fields.Selection([('draft', 'Draft'),('generate', 'Generate'),('difference', 'Difference'),('done', 'Done'),('noc','No Contract'),('error','Error')], 'Status', readonly=True,default='draft')
	invoice_id = fields.Many2one('account.invoice','Invoice')
	#note = fields.Text('Note',related='slip_id.note')
	#audit_result = fields.Selection('Audit Status',related='slip_id.audit_result',store=True)

	@api.model		
	def generate_invoices(self, nlimit=100):
		emp_pool = self.env['hr.employee']
		invoice_pool = self.env['account.invoice']
		invoice_ids = self.env['account.invoice']
		cron_draft_invoices = self.search([('state','=','draft')],limit=nlimit)		
		
		for cron_invoice in cron_draft_invoices:
			invoice_line_vals = []
			tax_line_vals = []
			month_days = 31.00
			for_month = ''

			partner_id = cron_invoice.post_id.partner_id.id
			post = self.env['sos.post'].search([('partner_id', '=', partner_id)])
			guard_recs = self.env['sos.post.jobs'].search([('post_id', '=', cron_invoice.post_id.id)])
			ds = cron_invoice.date_from
			dt = cron_invoice.date_to
			month_days = (dt-ds).days +1
			for_month = dt.strftime('%B-%Y')

			res = {
				'type': 'out_invoice',
				'company_id': 1,
				'account_id': 48,  # Receivable
				'payment_term_id': False,
				'fiscal_position_id': False,
				
				'partner_id': cron_invoice.post_id.partner_id.id,
				'post_id': cron_invoice.post_id.id,
				'project_id': cron_invoice.post_id.project_id.id,
				'center_id': cron_invoice.post_id.center_id.id,

				'for_month': for_month,
				'date_invoice': datetime.today().strftime('%Y-%m-%d'),
				'date_due': str(datetime.now() + relativedelta.relativedelta(day=31))[:10],
				'date_from': cron_invoice.date_from,
				'date_to': cron_invoice.date_to,
			}			
			invoice = invoice_pool.create(res)
			taxes_grouped = invoice.get_taxes_values()
			tax_grouped = {}

			for guard_rec in guard_recs:					
				ratepday = 1.00*guard_rec.rate/month_days	
				quantity = guard_rec.guards*month_days								
				#account = self.env['account.invoice.line'].get_invoice_line_account(self.type,guard_rec.product_id,self.fiscal_position_id,self.company_id)
				insurance = self.env['account.tax'].search([('amount_type','=','insurance')])
				
				invoice_line_vals.append({
					'product_id': guard_rec.product_id,
					'invoice_id': invoice.id,
					'name': guard_rec.product_id.partner_ref,					
					'account_id' : 94,   # Sales
					'guardrate': guard_rec.rate,
					'guards': guard_rec.guards,
					'quantity': guard_rec.guards*month_days,
					'month_days': month_days,
					'price_unit': ratepday,
					'invoice_line_tax_ids': guard_rec.post_id.taxrate_id,
		
				})
				#pdb.set_trace()				
				
				taxes = guard_rec.post_id.taxrate_id.compute_all(ratepday, invoice.currency_id, quantity, guard_rec.product_id, invoice.partner_id)['taxes']
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

				if invoice.post_id.insurance:
					tax_grouped[999]={
						'invoice_id': invoice.id,
						'name': 'Insurance Claim P/S.G Rs. %s'%invoice.post_id.insurance,
						'account_id' : 146,  # Insurance Claim
						'amount': int(invoice.post_id.insurance) * guard_rec.guards,
						'manual' : 10,
					}		
			
			invoice_lines = invoice.invoice_line_ids.browse([])
			for invoice_line in invoice_line_vals:
				invoice_lines += invoice_lines.new(invoice_line)

			tax_lines = invoice.tax_line_ids.browse([])
			for tax in tax_grouped.values():
				tax_lines += tax_lines.new(tax)
			
			invoice.tax_line_ids = tax_lines
			invoice.invoice_line_ids = invoice_lines
			cron_invoice.write({'state':'generate','invoice_id':invoice.id})