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

class ReportBiometricAttendance(models.AbstractModel):
	_name = 'report.sos_reports.report_biometricattendance'
	
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
		if rep == 'staff':
			if center_ids:
				recs = True
				for center_id in center_ids:
					line_ids = []
					center_id = self.env['sos.center'].search([('id','=',center_id)])
					emps = self.env['hr.employee'].search([('status', 'in',['new','active','onboarding']),('department_id','!=',29),('center_id','=',center_id.id),('is_guard','=', False)], order='code,department_id')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)], order='id')
						duty_status = '-'
						reason = '-'
						abt_reason = '-'
						#Attendance Condition
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							
							#Current Action Condition
							if attendance.current_action:
								if attendance.current_action == 'present':
									status = 'Present'
									if attendance.present_reason:
										if attendance.present_reason == 'in_field':
											reason = 'Field'
										if attendance.present_reason == 'out_station':
											reason = 'Out Station'
										if attendance.present_reason == 'visit':
											reason = 'Visit/Official Duty'		
								
								elif attendance.current_action == 'leave':
									status = 'Leave'
									reason = '-'
									abt_reason = '-'
								
								elif attendance.current_action == 'short_leave':
									status = 'Short Leave'
									reason = '-'
									abt_reason = '-'
									
								elif attendance.current_action == 'half_day_leave':
									status = 'Half Day'
									reason = '-'
									abt_reason = '-'	
									
								elif attendance.current_action == 'absent':
									status = 'Absent'
									
									if attendance.absent_reason:
										if attendance.absent_reason == 'leave':
											abt_reason = 'Leave'
										if attendance.absent_reason == 'short_leave':
											abt_reason = 'Short Leave'
										if attendance.absent_reason == 'half_day_leave':
											abt_reason = 'Half Day Leave'		
							else:
								status = 'Present'
								reason = '-'
								abt_reason = '-'
							# End of Current Action Condition
							
							#Duty Status Condition
							if attendance.duty_status:
								if attendance.duty_status == 'intime':
									duty_status = 'In Time'
								elif attendance.duty_status == 'late':
									duty_status = 'Late'		
								
						else: 
							att = "-"
							status = 'Absent'
							reason = '-'
							abt_reason = '-'
						#End of Attendance Condition
						line=({
							'ref' : emp.reference,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status,
							'present_reason' : reason,
							'absent_reason' : abt_reason,
							'duty_status' : duty_status, 
						})
						line_ids.append(line)
					
					if line_ids:	
						center_line =({
							'center' : center_id.name,
							'lines' : line_ids,
							})
						center_lines.append(center_line)
			
			# IF Project_ids
			if recs == False and project_ids:
				recs = True
				for project_id in project_ids:
					line_ids = []
					project_id = self.env['sos.project'].search([('id','=',project_id)])
					emps = self.env['hr.employee'].search([('status', 'in',['new','active','onboarding']),('department_id','!=',29),('project_id','=',project_id.id),('is_guard','=', False)], order='reference,department_id')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)],order='id')
						duty_status = '-'
						reason = '-'
						abt_reason = '-'
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							#Current Action Condition
							if attendance.current_action:
								if attendance.current_action == 'present':
									status = 'Present'
									if attendance.present_reason:
										if attendance.present_reason == 'in_field':
											reason = 'Field'
										if attendance.present_reason == 'out_station':
											reason = 'Out Station'
										if attendance.present_reason == 'visit':
											reason = 'Visit/Official Duty'		
								
								elif attendance.current_action == 'leave':
									status = 'Leave'
									reason = '-'
									abt_reason = '-'
									
								elif attendance.current_action == 'absent':
									status = 'Absent'
									
									if attendance.absent_reason:
										if attendance.absent_reason == 'leave':
											abt_reason = 'Leave'
										if attendance.absent_reason == 'short_leave':
											abt_reason = 'Short Leave'
										if attendance.absent_reason == 'half_day_leave':
											abt_reason = 'Half Day Leave'
											
								elif attendance.current_action == 'short_leave':
									status = 'Short Leave'
									reason = '-'
									abt_reason = '-'
									
								elif attendance.current_action == 'half_day_leave':
									status = 'Half Day'
									reason = '-'
									abt_reason = '-'
													
							else:
								status = 'Present'
								reason = '-'
								abt_reason = '-'
							# End of Current Action Condition
							
							#Duty Status Condition
							if attendance.duty_status:
								if attendance.duty_status == 'intime':
									duty_status = 'In Time'
								elif attendance.duty_status == 'late':
									duty_status = 'Late'
						else: 
							att = "-"
							status = 'Absent'
							reason = '-'
							abt_reason = '-'
						line=({
							'ref' : emp.reference,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status,
							'present_reason' : reason,
							'absent_reason' : abt_reason,
							'duty_status' : duty_status,
						})
						line_ids.append(line)
					if line_ids:	
						project_line =({
							'center' : project_id.name,
							'lines' : line_ids,
							})
						center_lines.append(project_line)
					
			# IF Department_ids
			if recs == False and department_ids:
				recs = True
				for department_id in department_ids:
					line_ids = []
					department_id = self.env['hr.department'].search([('id','=',department_id)])
					emps = self.env['hr.employee'].search([('status', 'in',['new','active','onboarding']),('department_id','=',department_id.id),('is_guard','=', False)], order='reference,department_id')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)], order='id')
						duty_status = '-'
						reason = '-'
						abt_reason = '-'
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							
							#Current Action Condition
							if attendance.current_action:
								if attendance.current_action == 'present':
									status = 'Present'
									if attendance.present_reason:
										if attendance.present_reason == 'in_field':
											reason = 'Field'
										if attendance.present_reason == 'out_station':
											reason = 'Out Station'
										if attendance.present_reason == 'visit':
											reason = 'Visit/Official Duty'		
								
								elif attendance.current_action == 'leave':
									status = 'Leave'
									abt_reason = '-'
									
								elif attendance.current_action == 'absent':
									status = 'Absent'
									abt_reason = '-'
									
									if attendance.absent_reason:
										if attendance.absent_reason == 'leave':
											abt_reason = 'Leave'
										if attendance.absent_reason == 'short_leave':
											abt_reason = 'Short Leave'
										if attendance.absent_reason == 'half_day_leave':
											abt_reason = 'Half Day Leave'
								
								elif attendance.current_action == 'short_leave':
									status = 'Short Leave'
									reason = '-'
									abt_reason = '-'
									
								elif attendance.current_action == 'half_day_leave':
									status = 'Half Day'
									reason = '-'
									abt_reason = '-'
													
							else:
								status = 'Present'
								reason = '-'
								abt_reason = '-'
							# End of Current Action Condition
							
							#Duty Status Condition
							if attendance.duty_status:
								if attendance.duty_status == 'intime':
									duty_status = 'In Time'
								elif attendance.duty_status == 'late':
									duty_status = 'Late'
						else: 
							att = "-"
							status = 'Absent'
							reason = '-'
							abt_reason = '-'
						line=({
							'ref' : emp.reference,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status,
							'present_reason' : reason,
							'absent_reason' : abt_reason,
							'duty_status' : duty_status,
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
					emps = self.env['hr.employee'].search([('status', 'in',['new','active','onboarding']),('id','=',employee_id.id),('is_guard','=', False)], order='reference')
					for emp in emps:
						attendance = self.env['sos.guard.attendance1'].search([('name', '>=', d1),('name', '<=', d2),('employee_id','=',emp.id)], order='id')
						duty_status = '-'
						reason = '-'
						abt_reason = '-'
						if attendance:
							attendance = attendance[0]
							att = localDate(self,strToDatetime(attendance.name)).strftime('%d/%m/%Y %H:%M:%S')
							
							#Current Action Condition
							if attendance.current_action:
								if attendance.current_action == 'present':
									status = 'Present'
									if attendance.present_reason:
										if attendance.present_reason == 'in_field':
											reason = 'Field'
										if attendance.present_reason == 'out_station':
											reason = 'Out Station'
										if attendance.present_reason == 'visit':
											reason = 'Visit/Official Duty'		
								
								elif attendance.current_action == 'leave':
									status = 'Leave'
									abt_reason = '-'
									
								elif attendance.current_action == 'absent':
									status = 'Absent'
									abt_reason = '-'
									
									if attendance.absent_reason:
										if attendance.absent_reason == 'leave':
											abt_reason = 'Leave'
										if attendance.absent_reason == 'short_leave':
											abt_reason = 'Short Leave'
										if attendance.absent_reason == 'half_day_leave':
											abt_reason = 'Half Day Leave'
								
								elif attendance.current_action == 'short_leave':
									status = 'Short Leave'
									reason = '-'
									abt_reason = '-'
									
								elif attendance.current_action == 'half_day_leave':
									status = 'Half Day'
									reason = '-'
									abt_reason = '-'
													
							else:
								status = 'Present'
								reason = '-'
								abt_reason = '-'
							# End of Current Action Condition
							
							#Duty Status Condition
							if attendance.duty_status:
								if attendance.duty_status == 'intime':
									duty_status = 'In Time'
								elif attendance.duty_status == 'late':
									duty_status = 'Late'
									
						else: 
							att = "-"
							status = 'Absent'
							reason = '-'
							abt_reason = '-'
						line=({
							'ref' : emp.reference,
							'emp_name' : emp.name,
							'post' : emp.current_post_id.name,
							'designation' : emp.job_id.name,
							'department' : emp.department_id.name,
							'name' : att,
							'status' : status,
							'present_reason' : reason,
							'absent_reason' : abt_reason,
							'duty_status' : duty_status,
							 
						})
						line_ids.append(line)
					employee_line =({
						'center' : employee_id.name,
						'lines' : line_ids,
						})
					center_lines.append(employee_line)							
						 	
			res = center_lines
		
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_biometricattendance')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Attendance" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_biometricattendance', docargs)
		
