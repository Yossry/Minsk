import pdb
from odoo import api, fields, models, _
from odoo import tools
from operator import itemgetter
import time
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d')
	
def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
	   
def dateToStr(ddate):
	return ddate.strftime('%Y-%m-%d')
			
def datetimeToStr(ddate):
	return ddate.strftime('%Y-%m-%d %H:%M:%S')
	
def utcDate(self, ddate):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_date = local_tz.localize(ddate, is_dst=False)
	utc_date = local_date.astimezone(utc)
	return utc_date
	
def localDate(self, utc_dt):
    user = self.env.user
    local_tz = timezone(user.tz)
    local_dt = utc_dt.replace(tzinfo=utc).astimezone(local_tz)
    return local_dt	


class ReportBiometricAttendanceSummary(models.AbstractModel):
	_name = 'report.sos_reports.report_biometric_attendancesummary'
	_description = 'Biometric Attendance Summary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def _get_day(self, start_date):
		res = []
		start_date = fields.Date.from_string(start_date)
		for x in range(0, 31):
			color = '#ababab' if start_date.strftime('%a') == 'Sun' else ''
			res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day , 'color': color})
			start_date = start_date + relativedelta(days=1)
		return res
		
	def _get_attendance_summary(self, start_date,end_date,empid):
		#Calculate the month's total days.
		last_day = 0
		sst_date = start_date
		if start_date:
			loc_date = fields.Datetime.from_string(start_date)
			loc_month = loc_date + relativedelta(day=1, months=+1, days=-1)
			last_day =loc_month.day
		 
		res = []
		b = []
		d1 = datetime.combine(fields.Date.from_string(start_date), time.min)
		d2 = datetime.combine(fields.Date.from_string(end_date), time.max)
		start_date = fields.Date.from_string(start_date)
		end_date = fields.Date.from_string(end_date)
		
		for index in range(0, 31):
			current = start_date + timedelta(index)
			res.append({'day': current.day, 'color': '', 'In': '-'})
			if current.strftime('%a') == 'Sun':
				res[index]['color'] = '#ababab'
				
		attendances = self.env['sos.guard.attendance1'].search([('employee_id', '=', empid), ('name', '>=', d1),	('name', '<=',d2)], order ='id desc')
		
		if attendances:
			p = 0 #present total variable
			l = 0 #leave total variable
			a = 0 #absent total variable 
			s = 0 #short leave total variable
			h = 0 #half leave total variable
			w = 0 # leave without pay variable
			lt = 0 # total Late Days
			empty_days = 0 # days containing '-'
			
			#Calculate total Present Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and (current_action is null or current_action ='present')",(d1,d2,empid));
			p_data = self.env.cr.dictfetchall()
			if p_data:
				 p = len(p_data) or 0
				 
			#Calculate total Leave Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and current_action ='leave'",(d1,d2,empid));
			l_data = self.env.cr.dictfetchall()
			if l_data:
				 l = len(l_data) or 0
				
			#Calculate total Absent Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and current_action ='absent'",(d1,d2,empid));
			a_data = self.env.cr.dictfetchall()
			if a_data:
				 a = len(a_data) or 0
				 
			#Calculate total Short Leave Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and current_action ='short_leave'",(d1,d2,empid));
			s_data = self.env.cr.dictfetchall()
			if s_data:
				 s = len(s_data) or 0
			
			#Calculate total Half Day Leave Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and current_action ='half_day_leave'",(d1,d2,empid));
			h_data = self.env.cr.dictfetchall()
			if h_data:
				 h = len(h_data) or 0
			
			#Calculate total Leave WithOut Pay Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and current_action ='lwop'",(d1,d2,empid));
			w_data = self.env.cr.dictfetchall()
			if w_data:
				 w = len(w_data) or 0	 	 	 	 	 
				 
			#Calculate total Late Days
			self.env.cr.execute("select distinct date_trunc('day', name) as date from sos_guard_attendance1 where name between %s and %s and employee_id = %s and duty_status='late'",(d1,d2,empid));
			lt_data = self.env.cr.dictfetchall()
			if lt_data:
				 lt = len(lt_data) or 0	 
			
			for attendance in attendances:
				if attendance.current_action not in ['leave','absent','short_leave','half_day_leave']:
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()		
					res[(check_in-start_date).days]['In'] = attendance.name and localDate(self,attendance.name).strftime('%H:%M') or '-'
					
				if attendance.current_action == 'leave':
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()
					res[(check_in-start_date).days]['In'] = 'L'
				
				if attendance.current_action == 'absent':
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()
					res[(check_in-start_date).days]['In'] = 'A'
					
				if attendance.current_action == 'short_leave':
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()
					res[(check_in-start_date).days]['In'] = 'S'
					
				if attendance.current_action == 'half_day_leave':
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()
					res[(check_in-start_date).days]['In'] = 'H'
					
				if attendance.current_action == 'lwop':
					check_in = fields.Datetime.from_string(attendance.name)
					check_in = fields.Datetime.context_timestamp(attendance, check_in).date()
					res[(check_in-start_date).days]['In'] = 'W'	
			
			if last_day > 0:
				#Check if appointment date is after the start date.
				emp_rec = self.env['hr.employee'].search([('id','=',empid)])
				#pdb.set_trace()
				emp_appointmentdate = fields.Date.from_string(emp_rec.appointmentdate)
				if emp_appointmentdate >fields.Date.from_string(sst_date):
					app_date = fields.Datetime.from_string(emp_appointmentdate)
					app_day =app_date.day
					empty_days = app_day - 1
				
				#Check if Terminate date is after the start date.
				if emp_rec.resigdate:
					emp_resigdate = emp_rec.resigdate
					if emp_resigdate > sst_date:
						resign_date = fields.Datetime.from_string(emp_resigdate)
						resign_day =resign_date.day
						empty_days = last_day - resign_day
					
				t = ((last_day) - (a + w + empty_days))		
			b.append({'M':last_day,'P':p,'LT':lt,'L':l,'A':a,'W':w,'S':s,'H':h,'T':t})	
		return res,b	

	def _get_data_from_report(self, data):
		start_date = data['form']['start_date'] and data['form']['start_date']
		end_date = data['form']['end_date'] and data['form']['end_date']
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
		department_ids = data['form']['department_ids'] and data['form']['department_ids'] or False
		employee_ids = data['form']['employee_ids'] and data['form']['employee_ids'] or False
		
		res = []
		emps = False
		if center_ids:
			self.env.cr.execute("select distinct employee_id from sos_guard_attendance1 where center_id in %s and name >= %s and name <= %s",(tuple(center_ids),start_date,end_date))
			emps = self.env.cr.dictfetchall()
		if not emps and project_ids:
			self.env.cr.execute("select distinct employee_id from sos_guard_attendance1 where project_id in %s and name >= %s and name <= %s",(tuple(project_ids),start_date,end_date))
			emps = self.env.cr.dictfetchall()
		if not emps and department_ids:
			self.env.cr.execute("select distinct employee_id from sos_guard_attendance1 where department_id in %s and name >= %s and name <= %s",(tuple(department_ids),start_date,end_date))
			emps = self.env.cr.dictfetchall()
		if not emps and employee_ids:
			self.env.cr.execute("select distinct employee_id from sos_guard_attendance1 where employee_id in %s and name >= %s and name <= %s",(tuple(employee_ids),start_date,end_date))
			emps = self.env.cr.dictfetchall()
		
		res.append({'data':[]})
		if not emps:
			raise UserError("Select Proper Input Data")

		for emp_id in emps:
			employee_rec = self.env['hr.employee'].search([('id','=',emp_id['employee_id'])])
			if employee_rec:
				res[0]['data'].append({
				'employee_id' : employee_rec.id,
				'emp': (employee_rec.code if employee_rec.code else '') + '/' + (employee_rec.name if employee_rec.name else ''),
				'display': self._get_attendance_summary(start_date,end_date,employee_rec.id)[0],
				'summary': self._get_attendance_summary(start_date,end_date,employee_rec.id)[1]
				})
		return res	

	@api.model
	def _get_report_values(self, docsid, data=None):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))	
		
		start_date = data['form']['start_date'] and data['form']['start_date']
		end_date = data['form']['end_date'] and data['form']['end_date']
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
		department_ids = data['form']['department_ids'] and data['form']['department_ids'] or False
		employee_ids = data['form']['employee_ids'] and data['form']['employee_ids'] or False
		recs = False

		if start_date and end_date:
			d1 = datetime.combine(fields.Date.from_string(start_date), time.min)
			d2 = datetime.combine(fields.Date.from_string(end_date), time.max)

		report_heading = ''
		res = {}
		line_ids = []
		
		if center_ids:
			recs = self.env['sos.center'].search([('id','in',center_ids)])
			for rec in recs:
				rec_name = rec.name if rec.name else ''
				report_heading = report_heading + rec_name + ","
		if project_ids:
			recs = self.env['sos.project'].search([('id','in',project_ids)])
			for rec in recs:
				rec_name = rec.name if rec.name else ''
				report_heading = report_heading + rec_name + ","
		if department_ids:
			recs = self.env['hr.department'].search([('id','in',department_ids)])
			for rec in recs:
				rec_name = rec.name if rec.name else ''
				report_heading = report_heading + rec_name + ","
		if employee_ids:
			recs = self.env['hr.employee'].search([('id','in',employee_ids)])
			for rec in recs:
				rec_name = rec.name if rec.name else ''
				report_heading = report_heading + rec_name + ","
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_reports.report_biometric_attendancesummary')
		
		#only for month days
		if data['form']['generate_month_entries']:
			month_recs = False
			month_recs = self._get_data_from_report(data)
			if month_recs:
				
				for m1_rec in month_recs:
					for m2_rec in m1_rec['data']: 
						_logger.info('.......Record for the Employee ... %r ... Created.....', m2_rec['employee_id'])
					
						m_vals = {
							'date' : start_date,
							'employee_id' : m2_rec['employee_id'], 
							'state' : 'draft',
							'total_days' : m2_rec['summary'][0]['M'],
							'present_days' : m2_rec['summary'][0]['T'],
							}
						self.env['hr.employee.month.attendance'].create(m_vals)
		docargs = {
			"doc_ids": [],
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"get_day": self._get_day(start_date),
			"get_data_from_report": self._get_data_from_report(data),
			"get_date_formate" : self.get_date_formate,
			"Report_Heading" : report_heading,
		}
		return docargs