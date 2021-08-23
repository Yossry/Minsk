import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from openerp import api, fields, models, _
from openerp.exceptions import UserError


class TaxAtSourceReport(models.AbstractModel):
	_name = 'report.sos_reports.tax_at_source_report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		line_ids = []
		res = {}
		payments = False
		grand_invoice_total = 0
		grand_tax_total = 0

		projects = self.env['sos.project'].search([])
		if projects:
			for project in projects:
				project_payment_total = 0
				invoice_total = 0
				invoices = False

				self.env.cr.execute("select sum(amount_total) as invoice_total from account_invoice where project_id = %s and date >= %s and date <= %s",(project.id,date_from, date_to))
				invoice_data = self.env.cr.dictfetchall()[0]
				invoice_total = int(0 if invoice_data['invoice_total'] is None else invoice_data['invoice_total'])

				invoices = self.env['account.invoice'].search([('project_id','=',project.id),('date_from','>=',date_from),('date_to','<=',date_to)])
				if invoices:
					if len(invoices) > 1:
						self.env.cr.execute("select payment_id from account_invoice_payment_rel where invoice_id in %s" %(tuple(invoices.ids),))
						payment_ids = self.env.cr.dictfetchall()

					if len(invoices) == 1:
						self.env.cr.execute("select payment_id from account_invoice_payment_rel where invoice_id = %s" % (invoices.id))
						payment_ids = self.env.cr.dictfetchall()

					payments = []
					for payment_id in payment_ids:
						payments.append(payment_id['payment_id'])

					project_payments = self.env['account.payment'].search([('payment_type', '=', 'inbound'), ('journal_id', '=', 30),('payment_date', '>=', date_from), ('payment_date', '<=', date_to),('id','in',payments)])
					if project_payments:
						self.env.cr.execute("select sum(amount) as payment_total from account_payment where id in  %s ",(tuple(project_payments.ids),))
						project_payment_data = self.env.cr.dictfetchall()[0]
						project_payment_total = int(0 if project_payment_data['payment_total'] is None else project_payment_data['payment_total'])

				grand_invoice_total = grand_invoice_total + invoice_total
				grand_tax_total =  grand_tax_total + project_payment_total

				line = {
					'project' : project.name,
					'invoice_total': invoice_total,
					'tax_at_source': project_payment_total,
					'receiving_month' : '',
					}
				line_ids.append(line)

		res = line_ids
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.tax_at_source_report')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"get_date_formate" : self.get_date_formate,
			'rep_data' : res,
			'grand_invoice_total' : grand_invoice_total,
			'grand_tax_total': grand_tax_total,
		}
		return docargs