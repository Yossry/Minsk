import pdb

import time
from datetime import date , datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
from odoo import api, fields, models, _
from odoo.exceptions import UserError

def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')

def localDate(self, utc_dt):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_dt = utc_dt.replace(tzinfo=utc).astimezone(local_tz)
	return local_dt			

class DailyAttendanceReport(models.AbstractModel):
	_name = 'report.hr_attendance_ext.report_dailyattendance'
	_description = "HR Daily Attendance Report"
	
	def _get_header_info(self, start_date, end_date):
		return {
			'start_date': start_date,
			'end_date': end_date,
		}
        
	@api.model
	def get_report_values(self, docsid, data=None):		
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		atts = []
		start_date = data['form']['start_date'] and data['form']['start_date']
		end_date = data['form']['end_date'] and data['form']['end_date']
		page_breaker = data['form']['page_breaker'] and data['form']['page_breaker'] or False
		employee_ids = data['form']['employee_ids'] and data['form']['employee_ids'] or False
		
		for emp in self.env['hr.employee'].browse(employee_ids):
			att_recs = self.env['hr.attendance'].search([('check_in','>=', start_date ),('check_in','<=',end_date),('employee_id','=', emp.id)], order='check_in')
			ats = []
			
			for rec in att_recs:
			
				worked_hours_time = "--"
				if rec.check_in and rec.check_out:
					duration = datetime.strptime(rec.check_out[:16],"%Y-%m-%d %H:%M")  - datetime.strptime(rec.check_in[:16],"%Y-%m-%d %H:%M")  
					totsec = duration.total_seconds()
					h = totsec//3600
					m = (totsec%3600) // 60
					worked_hours_time =  "%02d:%02d" %(h,m)
				
				att = {
					'date': rec.check_in[:10],
					'check_in': rec.check_in and localDate(self,strToDatetime(rec.check_in)).strftime('%H:%M') or '--',
					'check_out': rec.check_out and localDate(self,strToDatetime(rec.check_out)).strftime('%H:%M') or '--',					
					'worked_hours': worked_hours_time,
				}
				ats.append(att)
			atts.append({'emp':emp,'att':ats})

		report = self.env['ir.actions.report']._get_report_from_name('hr_attendance_ext.report_dailyattendance')
		employees = self.env['hr.employee']
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'docs': employees,
			'get_header_info': self._get_header_info(data['form']['start_date'], data['form']['end_date']),
			'Attendance' : atts or False,			
		}			
		return docargs
		
		
