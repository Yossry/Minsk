import pdb

import time
from datetime import date , datetime, timedelta
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


class AttendanceReport(models.AbstractModel):
	_name = 'report.hr_attendance_ext.report_attendance'
	_description = "HR Attendance Report"

	def _get_header_info(self, start_date):
		st_date = fields.Date.from_string(start_date)
		return {
			'start_date': fields.Date.to_string(st_date),
			'end_date': fields.Date.to_string(st_date + relativedelta(days=30)),
		}
        
	def _get_months(self, start_date):
		# it works for geting month name between two dates.
		res = []
		start_date = fields.Date.from_string(start_date)
		end_date = start_date + relativedelta(days=30)
		while start_date <= end_date:
			last_date = start_date + relativedelta(day=1, months=+1, days=-1)
			if last_date > end_date:
				last_date = end_date
			month_days = (last_date - start_date).days + 1
			res.append({'month_name': start_date.strftime('%B'), 'days': month_days})
			start_date += relativedelta(day=1, months=+1)
		return res
		
	def _get_day(self, start_date):
		res = []
		start_date = fields.Date.from_string(start_date)
		for x in range(0, 31):
			color = '#ababab' if start_date.strftime('%a') == 'Sat' or start_date.strftime('%a') == 'Fri' else ''
			res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day , 'color': color})
			start_date = start_date + relativedelta(days=1)
		return res

	def _get_attendance_summary(self, start_date, empid):
		res = []
		count = 0
		start_date = fields.Date.from_string(start_date)
		end_date = start_date + relativedelta(days=30)
		
		#res = [{'emp':emp,'days':[{'In':'.','Out':'.','Alert':'0'} for x in range(1,31)],'P':'-','T':'-','L':'-','A':'-','V':'-','R':'-',} 
		#	for emp in self.env['hr.employee'].browse(empids)]
		
		for index in range(0, 31):
			current = start_date + timedelta(index)
			res.append({'day': current.day, 'color': '', 'In': '-', 'Out': '-','Alert':'0'})
			if current.strftime('%a') == 'Sat' or current.strftime('%a') == 'Fri':
				res[index]['color'] = '#ababab'
		
		attendances = self.env['hr.attendance'].search([
			('employee_id', '=', empid), ('check_in', '<=', str(end_date)),	('check_in', '>=', str(start_date))
		])
		for attendance in attendances:
			check_in = fields.Datetime.from_string(attendance.check_in)
			check_in = fields.Datetime.context_timestamp(attendance, check_in).date()			
			res[(check_in-start_date).days]['In'] = attendance.check_in and localDate(self,strToDatetime(attendance.check_in)).strftime('%H:%M') or '--', 
			res[(check_in-start_date).days]['Out'] = attendance.check_out and localDate(self,strToDatetime(attendance.check_out)).strftime('%H:%M') or '--',
				
		holidays = self.env['hr.leave'].search([
			('employee_id', '=', empid), ('type', '=', 'remove'), ('date_from', '<=', str(end_date)), ('date_to', '>=', str(start_date))
		])
		for holiday in holidays:
			# Convert date to user timezone, otherwise the report will not be consistent with the
			# value displayed in the interface.
			date_from = fields.Datetime.from_string(holiday.date_from)
			date_from = fields.Datetime.context_timestamp(holiday, date_from).date()
			date_to = fields.Datetime.from_string(holiday.date_to)
			date_to = fields.Datetime.context_timestamp(holiday, date_to).date()
			for index in range(0, ((date_to - date_from).days + 1)):
				if date_from >= start_date and date_from <= end_date:
					res[(date_from-start_date).days]['color'] = holiday.holiday_status_id.color_name
					count+=1
				date_from += timedelta(1)
		self.emp_leave = count
		
		fmt = '%YYYY-%MM-%DD'
		sql = """select count(distinct to_char(check_in,'%s')) from hr_attendance where employee_id = %s 
			and check_in >= '%s' and check_in <= '%s'""" % (fmt,empid,str(start_date),str(end_date))
		
		self._cr.execute(sql)
		self.emp_present = int(self._cr.fetchall()[0][0])

		
		self.sum = count
		return res

	def _get_data_from_report(self, data):
		res = []
		Employee = self.env['hr.employee']
		if 'depts' in data:
			a = 5
			#for department in self.env['hr.department'].browse(data['depts']):
			#	res.append({'dept' : department.name, 'data': [], 'color': self._get_day(data['date_from'])})
			#	for emp in Employee.search([('department_id', '=', department.id)]):
			#	    res[len(res)-1]['data'].append({
			#	        'emp': emp.name,
			#	        'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
			#	        'sum': self.sum
			#	    })
		elif 'employee_ids' in data:
			res.append({'data':[]})
			for emp in Employee.browse(data['employee_ids']):
				res[0]['data'].append({
					'emp': emp.short_name,
					'display': self._get_attendance_summary(data['date'], emp.id),
					'sum': self.sum,
					'P': self.emp_present,
					'L': self.emp_leave,
				})			
		return res
	
	@api.model
	def get_report_values(self, docsid, data=None):			
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
			
		date = data['form']['date']
		employee_ids = data['form']['employee_ids'] or False
		atts = self.env['hr.attendance'].search([('check_in','>=',date ),('check_in','<=',date),('employee_id','in', employee_ids)], order='check_in')

		report = self.env['ir.actions.report']._get_report_from_name('hr_attendance_ext.report_attendance')
		employees = self.env['hr.employee']
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'docs': employees,
			'get_header_info': self._get_header_info(date),
			'get_months': self._get_months(date),
			'get_day': self._get_day(date),
			'get_data_from_report': self._get_data_from_report(data['form']),					
		}					
		return docargs
		
