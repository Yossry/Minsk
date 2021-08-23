import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportSalaryAdvisedPost(models.AbstractModel):
	_name = 'report.sos_payroll.report_salary_advisedpost'
	_description = 'Post Salary Advised Report'
	
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
		total_ud = 0
		total_net = 0
		total_pf = 0
		
		self.env.cr.execute("select distinct project_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		projects = self.env.cr.dictfetchall()

		for project in projects:
			project_id = project_obj.browse([project['project_id']])[0]
			advised = 0
			unadvised = 0
			ud = 0
			pf = 0
			
			sql = """select  sum(gpl.total) as total from guards_payslip gp, guards_payslip_line gpl, sos_project p
					where gpl.slip_id  = gp.id and gpl.code = 'BASIC' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and p.id = gp.project_id and p.id = %s and gp.advice_id is not NULL""" % (start_date,end_date,project_id.id,)	
			self.env.cr.execute(sql)		
			advised = self.env.cr.dictfetchall()[0]['total'] or 0
							
			sql = """select  sum(gpl.total) as total from guards_payslip gp, guards_payslip_line gpl, sos_project p
					where gpl.slip_id  = gp.id and gpl.code = 'BASIC' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and p.id = gp.project_id and p.id = %s and gp.advice_id is NULL""" % (start_date,end_date,project_id.id,)	
			self.env.cr.execute(sql)		
			unadvised = self.env.cr.dictfetchall()[0]['total'] or 0
			
							
			sql = """select  sum(gpl.total) as total from guards_payslip gp, guards_payslip_line gpl, sos_project p
					where gpl.slip_id  = gp.id and gpl.code = 'UD' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and p.id = gp.project_id and p.id = %s and gp.advice_id is not NULL""" % (start_date,end_date,project_id.id,)	
			self.env.cr.execute(sql)		
			ud = self.env.cr.dictfetchall()[0]['total'] or 0
			
			
			sql = """select  sum(gpl.total) as total from guards_payslip gp, guards_payslip_line gpl, sos_project p
					where gpl.slip_id  = gp.id and gpl.code = 'GPROF' and gp.date_from >= '%s' and gp.date_to <= '%s' 
					and p.id = gp.project_id and p.id = %s and gp.advice_id is not NULL""" % (start_date,end_date,project_id.id,)	
			self.env.cr.execute(sql)		
			pf = self.env.cr.dictfetchall()[0]['total'] or 0
			
			
			if advised > 0:
				total_advised += advised
			if unadvised > 0:
				total_unadvised += unadvised
			if ud > 0:
				total_ud += ud
			if pf > 0:
				total_pf += pf	
				
			res.append({
				'name': project_id.name,
				'advised': advised,
				'ud': ud,
				'total': advised + unadvised,
				'unadvised': unadvised,
				'pf': pf,
			})
		total_net = total_advised + total_unadvised
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_salary_advisedpost')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts_advised" : res or False,
			"Total_advised" : total_advised or 0,
			"Total_unadvised" : total_unadvised or 0,
			"Total_UD" : total_ud or 0,
			"Total_PF" : total_pf or 0,
			"Total_NET" : total_net or 0,
			"get_date_formate" : self.get_date_formate,
		}
		return docargs
