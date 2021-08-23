import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
from odoo import api, models
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter
from functools import reduce


class ReportSalaryInvoiceComp(models.AbstractModel):
	_name = 'report.sos_reports.report_salary_invoicecomp'
	_description = 'Salary _invoice Comparion Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')		
			
	@api.model
	def _get_report_values(self, docids, data=None):
		line_ids = []
		comp = {}
		
		total_saldays = 0
		total_sal_amt = 0
		total_invdays = 0
		total_inv_amt = 0
		total_diff_amt = 0
		
		project_ids = data['form']['project_ids'] or False
		center_ids = data['form']['center_ids'] or False
		target_move = data['form']['target_move'] or 'all'
		
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
				
					#if project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	

					self.env.cr.execute('''SELECT sum(quantity) qty ,sum(gpl.total) tot from guards_payslip gp ,guards_payslip_line gpl \
						where gp.id = gpl.slip_id and gpl.code = 'BASIC' and gpl.post_id = %s and gp.date_from >= %s and gp.date_to <= %s''',(post.id,date_from,date_to))
					salary = self.env.cr.fetchall()

					#if project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	

					self.env.cr.execute('''SELECT sum(quantity) qty ,sum(price_subtotal) tot from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s''',(post.id,date_from,date_to))

					invoice = self.env.cr.fetchall()
				
					if target_move == 'all' or (target_move == 'diff' and salary[0][0] != invoice[0][0]) or (target_move == 'more' and salary[0][0] > invoice[0][0])  or (target_move == 'less' and salary[0][0] < invoice[0][0]):
				
						saldays = salary[0][0] or 0
						saltotal = salary[0][1] or 0
						invdays = invoice[0][0] or 0
						invtotal = invoice[0][1] or 0
					
						total_saldays += saldays
						total_sal_amt += saltotal
						total_invdays += invdays
						total_inv_amt += invtotal
						total_diff_amt += invdays - saldays
				
						res=({
							'name': post.name,
							'saldays': saldays,
							'saltotal': saltotal,
							'invdays': invdays,
							'invtotal': invtotal,
							'diff': invdays - saldays,
						})			
						result.append(res)
				result1 = result
		
				total_byprj.update({
					'saldays': reduce(lambda x, obj: x + obj['saldays'], result1, 0),
					'saltotal': reduce(lambda x, obj: x + obj['saltotal'], result1, 0),
					'invdays': reduce(lambda x, obj: x + obj['invdays'], result1, 0),
					'invtotal': reduce(lambda x, obj: x + obj['invtotal'], result1, 0),
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
				
					#if post.project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	

					self.env.cr.execute('''SELECT sum(quantity) qty ,sum(gpl.total) tot from guards_payslip gp ,guards_payslip_line gpl \
						where gp.id = gpl.slip_id and gpl.code = 'BASIC' and gpl.post_id = %s and gp.date_from >= %s and gp.date_to <= %s''',(post.id,date_from,date_to))
					salary = self.env.cr.fetchall()

					#if post.project_id.id == 30:
					#	date_from = str(datetime.datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
					#	date_to = str(datetime.datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	

					self.env.cr.execute('''SELECT sum(quantity) qty ,sum(price_subtotal) tot from account_invoice acinv ,account_invoice_line acinvl \
						where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s''',(post.id,date_from,date_to))

					invoice = self.env.cr.fetchall()
				
					if target_move == 'all' or (target_move == 'diff' and salary[0][0] != invoice[0][0]) or (target_move == 'more' and salary[0][0] > invoice[0][0])  or (target_move == 'less' and salary[0][0] < invoice[0][0]):
				
						saldays = salary[0][0] or 0
						saltotal = salary[0][1] or 0
						invdays = invoice[0][0] or 0
						invtotal = invoice[0][1] or 0
					
						total_saldays += saldays
						total_sal_amt += saltotal
						total_invdays += invdays
						total_inv_amt += invtotal
						total_diff_amt += invdays - saldays
				
						res=({
							'name': post.name,
							'saldays': saldays,
							'saltotal': saltotal,
							'invdays': invdays,
							'invtotal': invtotal,
							'diff': invdays - saldays,
						})			
						result.append(res)
				result1 = result
		
				total_byprj.update({
					'saldays': reduce(lambda x, obj: x + obj['saldays'], result1, 0),
					'saltotal': reduce(lambda x, obj: x + obj['saltotal'], result1, 0),
					'invdays': reduce(lambda x, obj: x + obj['invdays'], result1, 0),
					'invtotal': reduce(lambda x, obj: x + obj['invtotal'], result1, 0),
				})
					 		
				line=({
					'name' : center_id.name,
					'posts' : result1,
					})
				line_ids.append(line)
			comp = line_ids
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_salary_invoicecomp')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Comp_Vals" : comp or False,
			"Total_Saldays" : total_saldays, 
			"Total_Sal_Amt" : total_sal_amt,
			"Total_Invdays" : total_invdays,
			"Total_Inv_Amt" : total_inv_amt,
			"Total_Diff_Amt" : total_diff_amt,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs
		
