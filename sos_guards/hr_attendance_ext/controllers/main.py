# -*- coding: utf-8 -*-
import time
from odoo.addons.mail.controllers.main import MailController
from datetime import date , datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta
from odoo import fields, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import release

# http://pythonhosted.org/ranking/      easy_install ranking
import ranking 
import pdb

def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')

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

def parse_date(td):
	resYear = float(td.days)/365.0                  
	resMonth = (resYear - int(resYear))*365.0/30.0 
	resDays = int((resMonth - int(resMonth))*30)
	resYear = int(resYear)
	resMonth = int(resMonth)
	return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")

def compute_duration(ddate):
	start = datetime.strptime(ddate,OE_DFORMAT)
	end = datetime.strptime(time.strftime(OE_DFORMAT),OE_DFORMAT)	
	delta = end - start
	return parse_date(delta)
		
class AttendanceDashboard(http.Controller):

	@http.route('/attendance_dashboard/data', type='json', auth='user')
	def attendance_dashboard_data(self, userid=0):
		
		#if not request.env.user.has_group('base.group_erp_manager'):
		#	raise AccessError("Access Denied")
		
		cr = request.cr
		if userid == 0:
			userinfo = request.env['hr.employee'].search([('user_id','=',request.env.user.id)])
		else:	
			userinfo = request.env['hr.employee'].search([('code','=',str(userid).zfill(4))])
		
		if not userinfo:
			userinfo = request.env['hr.employee'].search([('user_id','=',request.env.user.id)])
			
		if not userinfo:	
			userinfo = request.env['hr.employee'].search([('code','=','0003')])
			
		attendance = [{'name':month,'days':[{'In':'.','Out':'.','Alert':'0','TT':'','Color':''} for x in range(1,32)],'P':0,'T':0,'L':0,'A':0,'V':0,'R':0,} 
			for month in ['January','February','March','April','May','June','July','August','September','October','November','December']]
	
		att_recs = request.env['hr.attendance'].search([('employee_id','=',userinfo.id),'|',('check_in','>=','2018-01-01'),('check_out','>=','2018-01-01')],order='check_in')
		for att in att_recs:
			dt = strToDatetime(att.check_in or att.check_out)
			month = int(dt.strftime('%m'))-1
			day = int(dt.strftime('%d'))-1
			
			attendance[month]['days'][day]['In'] = att.check_in and localDate(request,strToDatetime(att.check_in)).strftime('%H:%M') or '--'
			attendance[month]['days'][day]['Out'] = att.check_out and localDate(request,strToDatetime(att.check_out)).strftime('%H:%M') or '--'
									
			worked_hours_time = "--"
			if att.check_in and att.check_out:
				duration = datetime.strptime(att.check_out[:16],"%Y-%m-%d %H:%M")  - datetime.strptime(att.check_in[:16],"%Y-%m-%d %H:%M")  
				totsec = duration.total_seconds()
				h = totsec//3600
				m = (totsec%3600) // 60
				worked_hours_time =  "%02d:%02d" %(h,m)
	
	
			tooltip = "In Time :         " + (att.check_in and localDate(request,strToDatetime(att.check_in)).strftime('%Y-%m-%d %H:%M') or '--')
			tooltip = tooltip + "\nOut Time :     " + (att.check_out and localDate(request,strToDatetime(att.check_out)).strftime('%Y-%m-%d %H:%M') or '--')
			tooltip = tooltip + "\nWork Time : " + worked_hours_time
			
			
			attendance[month]['days'][day]['TT'] = tooltip
		
		leave_recs = request.env['hr.leave'].search([('employee_id','=',userinfo.id),('date_from','>=','2018-01-01')],order='date_from')
		emp_leave_total = 0
		for leave in leave_recs:	
			leave_days = abs(int(leave.number_of_days))
			for i in range(leave_days):				
				dt = strToDatetime(leave.date_from) + relativedelta(days=i)
				month = int(dt.strftime('%m'))-1
				day = int(dt.strftime('%d'))-1
			
				attendance[month]['days'][day]['In'] = leave.holiday_status_id.code
				attendance[month]['days'][day]['Color'] = leave.holiday_status_id.color_name
				attendance[month]['days'][day]['Out'] = 'L'
			
				tooltip = "Leave Type :         " + leave.holiday_status_id.name
				if leave.name:
					tooltip = tooltip + "\nDesc :     " + leave.name
				attendance[month]['days'][day]['TT'] = tooltip	
				
			attendance[month]['L'] += leave_days
			emp_leave_total += leave_days
			
		sql = """select * from hr_attendance_report_employee_present where employee = %s """ % (userinfo.id,)
		cr.execute(sql)
		
		if cr.rowcount > 0:
			emp_present = cr.fetchall()[0]
			emp_present = [0 if v is None else int(v) for v in emp_present]
			emp_present.pop(0)
		else:
			emp_present = [0 for i in range(12)]
			
		emp_present_total = sum(emp_present)
					
		for i in range(12):
			attendance[i]['P'] = emp_present[i]
		
			
		data =  {
			'emp': {
				'empid' : userinfo.code,				
			},
			'empinfo': {
				'english_name' : userinfo.english_name or '',
				'code' : userinfo.code or '',
				'designation' : userinfo.job_id and userinfo.job_id.name or '',
				'department' : userinfo.department_id and userinfo.department_id.name or '',
				'nationality' : userinfo.country_id and userinfo.country_id.name or '',
				'joining_date' : userinfo.joining_date or '',
				'duration' : userinfo.joining_date and compute_duration(userinfo.joining_date) or '-',
				'reporting' : userinfo.parent_id and str(userinfo.parent_id.sudo().code) + ' - ' + userinfo.parent_id.sudo().short_name or '',	
				
				'days': ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20', 						'21','22','23','24','25','26','27','28','29','30','31'],							
				'attendance' : attendance,
				
				'emp_present_total': emp_present_total, 
				'emp_leave_total': emp_leave_total,
			},			
		}
		
		return data
		
		
		
