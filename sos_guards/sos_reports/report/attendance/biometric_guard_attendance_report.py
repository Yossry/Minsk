import pdb
from openerp import api, models
from openerp import tools
from operator import itemgetter
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()
	
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

class ReportBiometricGuardAttendance(models.AbstractModel):
	_name = 'report.sos_reports.report_guard_biometricattendance'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.multi
	def render_html(self, data=None):
		rep = to_day = data['form']['rep'] and data['form']['rep']
		to_day = data['form']['to_day'] and data['form']['to_day']
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
		department_ids = data['form']['department_ids'] and data['form']['department_ids'] or False
		employee_ids = data['form']['employee_ids'] and data['form']['employee_ids'] or False
		
		recs = False
		d1= to_day + ' 00:00:01'
		d2= to_day + ' 23:59:59'
		
		res = {}
		center_lines = []
		if rep == 'guard':
			# IF Center_ids
			if center_ids:
				recs = True
				for center_id in center_ids:
					line_ids = []
					center_id = self.env['sos.center'].search([('id','=',center_id)])
					self.env.cr.execute("SELECT distinct post_id FROM sos_attendance_device where center_id = %s and state='done'" %(center_id.id))
					posts = self.env.cr.fetchall()
					post_ids = [i for (i,) in posts]
					
					emps = self.env['hr.employee'].search([('department_id','=',29),('center_id','=',center_id.id),('is_guard','=', True),('current','=',True),('current_post_id','in',post_ids)], order='code')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)], order='id')
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							status = 'Present'
						else: 
							att = "-"
							status = 'Absent'
						line=({
							'ref' : emp.code,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status, 
						})
						line_ids.append(line)
					if line_ids:	
						center_line =({
							'center' : center_id.name,
							'lines' : line_ids,
							})
						center_lines.append(center_line)
			
			# IF Project_ids
			if project_ids:
				recs = True
				for project_id in project_ids:
					line_ids = []
					project_id = self.env['sos.project'].search([('id','=',project_id)])
					
					self.env.cr.execute("SELECT distinct post_id FROM sos_attendance_device where project_id = %s and state='done'" %(project_id.id))
					posts = self.env.cr.fetchall()
					post_ids = [i for (i,) in posts]
					
					emps = self.env['hr.employee'].search([('department_id','=',29),('project_id','=',project_id.id),('is_guard','=', True),('current','=',True),('current_post_id','in',post_ids)], order='code')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)],order='id')
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							status = 'Present'
						else: 
							att = "-"
							status = 'Absent'
						line=({
							'ref' : emp.code,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status, 
						})
						line_ids.append(line)
					if line_ids:	
						project_line =({
							'center' : project_id.name,
							'lines' : line_ids,
							})
						center_lines.append(project_line)
					
			# IF Department_ids
			if department_ids:
				recs = True
				for department_id in department_ids:
					line_ids = []
					department_id = self.env['hr.department'].search([('id','=',department_id)])
					emps = self.env['hr.employee'].search([('department_id','=',department_id.id),('is_guard','=', True),('current','=', True)], order='code')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)],order='id')
						
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							status = 'Present'
						else: 
							att = "-"
							status = 'Absent'
						line=({
							'ref' : emp.code,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status, 
						})
						line_ids.append(line)
					if line_ids:
						department_line =({
							'center' : department_id.name,
							'lines' : line_ids,
							})
						center_lines.append(department_line)
					
			# IF Employee_ids
			if recs == False and employee_ids:
				recs = True
				for employee_id in employee_ids:
					line_ids = []
					employee_id = self.env['hr.employee'].search([('id','=',employee_id)])
					emps = self.env['hr.employee'].search([('id','=',employee_id.id),('is_guard','=', True),('current','=', True)], order='code')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)])
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							status = 'Present'
						else: 
							att = "-"
							status = 'Absent'
						line=({
							'ref' : emp.code,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status, 
						})
						line_ids.append(line)
					employee_line =({
						'center' : employee_id.name,
						'lines' : line_ids,
						})
					center_lines.append(employee_line)								
						 	
			res = center_lines
		
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_guard_biometricattendance')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Attendance" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_guard_biometricattendance', docargs)
		
