import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class ReportPFEmployeeStatement(models.AbstractModel):
	_name = 'report.sos_provident_fund.report_pf_employeestatement'
	_description = 'PF Employee Statement Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		employee_id = data['form']['employee_id'] and data['form']['employee_id'][0] or False
		data_recs = False
		sub_total = 0
		total = 0
		
		if employee_id:
			emp = self.env['hr.employee'].search([('id','=',employee_id),'|',('current','=',True),('current','=',False)])
			personal_info = ({
				'name': emp.name,
				'ref': emp.code,
				'cnic': emp.cnic,
				'status' : 'Current' if emp.current else '',
				})
			
			data_recs = self.env['guards.payslip.line'].search([('employee_id','=',employee_id),('code','=','GPROF')], order='id')
			if data_recs:
				for rec in data_recs:
					sub_total = sub_total + abs(rec.amount)
				total = total + (sub_total*2)

		report = self.env['ir.actions.report']._get_report_from_name('sos_provident_fund.report_pf_employeestatement')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"recs": data_recs or False,
			"sub_total" : sub_total,
			"total" : total,
			'info' : personal_info,
			"get_date_formate" : self.get_date_formate,
		}