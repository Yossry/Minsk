import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp.tools.translate import _
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class ReportCompSummaryCenter(models.AbstractModel):
	_name = 'report.sos_reports.report_compsummarycenter'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_period1(self,date_from):
		dt = datetime.strptime(date_from,'%Y-%m-%d')
		dt = str(dt + relativedelta.relativedelta(months=-1))[:10]
		dt = datetime.strptime(dt,'%Y-%m-%d')
		
		period = self.env['sos.period'].search([('date_start','=',dt)])
		return period
	
	def get_period2(self,date_from):
		period = self.env['sos.period'].search([('date_start','=',date_from)])
		return period
				
			
	@api.multi
	def render_html(self, data=None):
	
		prid1 = self.get_period1(data['form']['date_from']).date_start
		prid2 = self.get_period2(data['form']['date_from']).date_start
		res = []
		prev_total = 0
		current_total = 0
		diff_total = 0
			
		
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		if center_ids:
			center_ids = self.env['sos.center'].search([('id','in',center_ids)])
		if not center_ids:
			center_ids = self.env['sos.center'].search([])
		
		for center in center_ids:
			self.env.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.date_from = %s and gp.center_id = %s and code = %s and state in ('done')",(prid1,center.id,'BASIC'))
			salary_data = self.env.cr.dictfetchall()[0]
			prev_salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
			
			self.env.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.date_from = %s and gp.center_id = %s and code = %s and state in ('done')",(prid2,center.id,'BASIC'))
			salary_data = self.env.cr.dictfetchall()[0]
			salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
			
			
			diff = (salary-prev_salary)

			res.append({
				'center_name': center.name,
				'amount': salary or 0,
				'amount_prev': prev_salary or 0,
				'diff': diff or 0,
			})

			prev_total += prev_salary
			current_total += salary
			diff_total += diff		
							
	
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_compsummarycenter')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Period1" : self.get_period1,
			"Period2" : self.get_period2,
			"Records" : res or False,
			"Prev_Total" : prev_total or 0,
			"Current_Total" : current_total or 0,
			"Diff_Total" : diff_total or 0,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_compsummarycenter', docargs)
		
