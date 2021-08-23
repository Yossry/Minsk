import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportSalaryAdvisedCenter(models.AbstractModel):
	_name = 'report.sos_payroll.report_salary_advisedcenter'
	_description = 'Center Salary Advised Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
			
	@api.model
	def _get_report_values(self, docids, data=None):
		start_date = data['form']['date_from'] or False
		end_date = data['form']['date_to'] or False
		
		payslip_obj = self.env['guards.payslip']
		center_obj = self.env['sos.center']
		
		res = []
		total_advised = 0
		total_unadvised = 0
		total_ud = 0
		total_net = 0
		
		self.env.cr.execute("select distinct center_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		centers = self.env.cr.dictfetchall()

		for center in centers:
			center_id = center_obj.browse([center['center_id']])[0]

			self.env.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'BASIC' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.env.cr.dictfetchall()
			advised = lines[0]['total'] or 0

			self.env.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is NULL and code = 'BASIC' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.env.cr.dictfetchall()
			unadvised = lines[0]['total'] or 0

			self.env.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'UD' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.env.cr.dictfetchall()
			ud = lines[0]['total'] or 0
			
			if advised:
				total_advised += advised
			if unadvised:
				total_unadvised += unadvised
			if ud:
				total_ud += ud
				
			res.append({
				'name': center_id.name,
				'advised': advised,
				'ud': ud,
				'total': advised + unadvised,
				'unadvised': unadvised,
			})
		total_net = total_advised + total_unadvised
	
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_salary_advisedcenter')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers_advised" : res or False,
			"Total_advised" : total_advised or 0,
			"Total_unadvised" : total_unadvised or 0,
			"Total_UD" : total_ud or 0,
			"Total_NET" : total_net or 0,
			"get_date_formate" : self.get_date_formate,
		}
		
		return docargs
		
