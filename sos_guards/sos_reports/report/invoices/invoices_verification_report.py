import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportInvoicesVerification(models.AbstractModel):
	_name = 'report.sos_reports.report_invoicesverification'
	_description = 'Invoices Verifications Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		project_id = data['form']['project_id'] and data['form']['project_id'][0]
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		line_ids = []
		res = {}
		
		invoice_obj = self.env['account.invoice']
		post_obj = self.env['sos.post']
		
		if project_id:
			post_ids = post_obj.search([('project_id','=',project_id)])
			for post_id in post_ids:
				invoices = invoice_obj.search([('post_id','=',post_id.id),('date_from','=',date_from),('date_to','=',date_to)],order = 'date_from')
				line=({
					"name" : post_id.name,
					"invoices" : invoices,
					})
				line_ids.append(line)
			res = line_ids
			
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_invoicesverification')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Invoices" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs
		
