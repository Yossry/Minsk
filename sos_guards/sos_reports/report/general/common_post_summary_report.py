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


class ReportCommonPostSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_common_summarypost'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.multi
	def render_html(self, data=None):
		
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		
		bankcharges_amount = 0
		
		center_lines = []
		res = {}
		tax_amount = 0
		
		if center_ids:
			centers = self.env['sos.center'].search([('id','in', center_ids)])
			for center in centers:
				project_lines = []
				project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
				
				if project_ids:
					projects = self.env['sos.project'].search([('id','in',project_ids)])
					
					for project in projects:
						posts = self.env['sos.post'].search([('center_id','=',center.id),('project_id','=',project.id),('active','=', True)])
						line_ids = []
			
						for post in posts:
							self.env.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 35 \
											and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
							bankcharges_data = self.env.cr.dictfetchall()[0]
							bankcharges = int(0 if bankcharges_data['amount'] is None else bankcharges_data['amount'])

							line = ({
								'post_name': post.name,
								'bankcharges': bankcharges or 0,
								})
								
							bankcharges_amount += bankcharges
						project_line = ({
								"project_name" : project.name,
								"posts" : line_ids,
								})
						project_lines.append(project_line)
		
				center_line = ({
						"center_name" : center.name,
						"projects" : project_lines,
						})
				center_lines.append(center_line)
			res = center_lines or False	
		
			
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_common_summarypost')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"BankCharges" : bankcharges_amount or 0,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_common_summarypost', docargs)
		
