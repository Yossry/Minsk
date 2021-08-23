import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, models
from odoo import tools
from operator import itemgetter
from functools import reduce


class ReportAttendanceInvoiceComp(models.AbstractModel):
	_name = 'report.sos_reports.report_attendance_invoicecomp'
	_description = 'Attendance Invoice Comparsion Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')		
			
	@api.model
	def _get_report_values(self, docids, data=None):
		line_ids = []
		comp = {}
		
		total_attdays = 0
		total_invdays = 0
		total_diff_days = 0
		
		project_ids = data['form']['project_ids'] or False
		center_ids = data['form']['center_ids'] or False
		
		## For Projects ##
		if project_ids:
			project_ids = self.env['sos.project'].search([('id','in', project_ids)])
			
			for project_id in project_ids:
				result = []
				total_byprj = {}
				post_ids = self.env['sos.post'].search([('project_id','=', project_id.id),'|',('active','=',True),'&',('enddate' ,'>=', data['form']['date_from'] ),('enddate', '<=',  data['form']['date_to'])])
		
				for post in post_ids:
				
					date_from = data['form']['date_from'] or '2013-10-01'
					date_to = data['form']['date_to'] or  '2013-10-31'
					remarks = ''
				
					#if project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	

					self.env.cr.execute("SELECT sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total \
										FROM sos_guard_attendance t where t.post_id =%s and t.name >= %s and t.name <=%s ",(post.id, date_from, date_to))
					attendance = self.env.cr.dictfetchall()

					#if project_id.id in (30,32):
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	

					self.env.cr.execute("SELECT sum(quantity) as qty from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s and acinv.inv_type != 'credit'",(post.id,date_from,date_to))
					invoice = self.env.cr.dictfetchall()
					
					## Credit Notes
					self.env.cr.execute("SELECT sum(quantity) as qty from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s and acinv.inv_type ='credit'",(post.id,date_from,date_to))
					credit_invoice = self.env.cr.dictfetchall()
				
					
					attdays = attendance[0]['total'] or 0
					crddays = credit_invoice[0]['qty'] or 0
					invdays = invoice[0]['qty'] or 0
					invdays = invdays - crddays
				
					total_attdays += attdays
					total_invdays += invdays
					total_diff_days += invdays - attdays
					
					if (invdays - attdays) == 0:
						remarks = 'OK'
					if (invdays - attdays) > 0:
						remarks = 'Less attendance'
					if (invdays - attdays) < 0:
						remarks = 'Extra attendance'	
			
					res=({
						'name': post.name,
						'region' : post.center_id and post.center_id.name or '',
						'attdays': attdays,
						'invdays': invdays,
						'diff': invdays - attdays,
						'remarks' : remarks,
					})			
					result.append(res)
				result1 = result
		
				total_byprj.update({
					'attdays': reduce(lambda x, obj: x + obj['attdays'], result1, 0),
					'invdays': reduce(lambda x, obj: x + obj['invdays'], result1, 0),
				})
					 		
				line=({
					'name' : project_id.name,
					'posts' : result1,
					})
				line_ids.append(line)
			comp = line_ids
			
		
		## For Centers ##
		if not project_ids:				
			center_ids = self.env['sos.center'].search([('id','in', center_ids)])
			
			for center_id in center_ids:
				result = []
				total_byprj = {}
				
				center_post_ids = self.env['sos.post'].search([('center_id','=', center_id.id),'|',('active','=',True),'&',('enddate' ,'>=', data['form']['date_from'] ),('enddate', '<=',  data['form']['date_to'])])
		
				for post in center_post_ids:
				
					date_from = data['form']['date_from'] or '2013-10-01'
					date_to = data['form']['date_to'] or  '2013-10-31'
					remarks = ''
				
					#if post.project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	

					self.env.cr.execute("SELECT sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total \
										FROM sos_guard_attendance t where t.post_id =%s and t.name >= %s and t.name <=%s ",(post.id, date_from, date_to))
					attendance = self.env.cr.dictfetchall()
					
					#if post.project_id.id in (30,32):
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	

					self.env.cr.execute("SELECT sum(quantity) qty from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s and acinv.inv_type != 'credit'",(post.id,date_from,date_to))
					invoice = self.env.cr.dictfetchall()
					
					## Credit Note
					self.env.cr.execute("SELECT sum(quantity) qty from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s and acinv.inv_type ='credit'",(post.id,date_from,date_to))
					credit_invoice = self.env.cr.dictfetchall()
					
				
					attdays = attendance[0]['total'] or 0
					crddays = credit_invoice[0]['qty'] or 0
					invdays = invoice[0]['qty'] or 0
					invdays = invdays - crddays
				
					total_attdays += attdays
					total_invdays += invdays
					total_diff_days += invdays - attdays
					
					
					if (invdays - attdays) == 0:
						remarks = 'OK'
					if (invdays - attdays) > 0:
						remarks = 'Less attendance'
					if (invdays - attdays) < 0:
						remarks = 'Extra attendance'
			
					res=({
						'name': post.name,
						'region' : post.project_id and post.project_id.name or '',
						'attdays': attdays,
						'invdays': invdays,
						'diff': invdays - attdays,
						'remarks' : remarks,
					})			
					result.append(res)
				result1 = result
		
				total_byprj.update({
					'attdays': reduce(lambda x, obj: x + obj['attdays'], result1, 0),
					'invdays': reduce(lambda x, obj: x + obj['invdays'], result1, 0),
				})
					 		
				line=({
					'name' : center_id.name,
					'posts' : result1,
					})
				line_ids.append(line)
			comp = line_ids	
	
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_attendance_invoicecomp')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Comp_Vals" : comp or False,
			"Total_Attdays" : total_attdays, 
			"Total_Invdays" : total_invdays,
			"Total_Diff_Days" : total_diff_days,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs
