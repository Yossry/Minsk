import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportSalaryAdvisedBase(models.AbstractModel):
	_name = 'report.sos_payroll.report_salary_advisedbase'
	_description = 'Base Advised Salary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		start_date = data['form']['date_from'] or False
		end_date = data['form']['date_to'] or False
		
		payslip_obj = self.env['guards.payslip']
		project_obj = self.env['sos.project']
		
		res = []
		total_advised = 0
		total_unadvised = 0
		total_net = 0
		
		self.env.cr.execute("select distinct project_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		projects = self.env.cr.dictfetchall()
		
		for project in projects:
			project_id = project_obj.browse([project['project_id']])[0]

			self.env.cr.execute("select sum(t.total) as total from guards_payslip pl, guards_payslip_line t \
							where t.slip_id = pl.id and t.code='NET' and pl.project_id = %s and pl.advice_id is not NULL and pl.date_from >= %s and pl.date_to <= %s", (project['project_id'],start_date,end_date))
			lines = self.env.cr.dictfetchall()
			advised = lines[0]['total']
			
			self.env.cr.execute("select sum(t.total) as total from guards_payslip pl, guards_payslip_line t \
							where t.slip_id = pl.id and t.code='NET' and pl.project_id = %s and pl.advice_id is NULL and pl.date_from >= %s and pl.date_to <= %s", (project['project_id'],start_date,end_date))
			lines = self.env.cr.dictfetchall()
			unadvised = lines[0]['total']
			
			if advised:
				total_advised += advised
			if unadvised:
				total_unadvised += unadvised
			res.append({
				'name': project_id.name,
				'advised': advised,
				'unadvised': unadvised,
			})
		total_net = total_advised + total_unadvised	
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_salary_advisedbase')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Recs" : res or False,
			"Total_advised" : total_advised or 0,
			"Total_unadvised" : total_unadvised or 0,
			"Total_net" : total_net or 0,
			"get_date_formate" : self.get_date_formate,
		}
