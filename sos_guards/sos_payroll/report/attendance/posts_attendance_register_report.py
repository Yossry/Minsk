import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportPostsAttendanceRegister(models.AbstractModel):
	_name = 'report.sos_payroll.report_postsattendance_register'
	_description = 'Post Attendance Register Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def _get_center_project_posts(self, project_id,center_id):
			
		posts_obj = self.env['sos.post']
		domain = [('center_id', '=', center_id),('project_id', '=', project_id),('active','=',True)]				
		post_ids = posts_obj.search(domain)
		return post_ids
		
	@api.model
	def _get_report_values(self, docids, data=None):
		
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		center_id = data['form']['center_id'] and  data['form']['center_id'][0] or False
		project_id= data['form']['project_id'] and data['form']['project_id'][0] or False
		
		attendance_obj = self.env['sos.guard.attendance']
		employee_obj = self.env['hr.employee']
		
		line_ids = []
		res = {}
		total = 0
		
		posts_obj = self.env['sos.post']
		domain = [('center_id', '=', center_id),('project_id', '=', project_id),('active','=',True)]				
		post_ids = posts_obj.search(domain)
		
		for post_id in post_ids:
			employee_ids = []
			guards = []

			self.env.cr.execute("select distinct employee_id from sos_guard_attendance where post_id=%s and name >= %s and name <=  %s",(post_id.id,date_from,date_to))
			guards_rec = self.env.cr.dictfetchall()
				
			for x in guards_rec:
				employee_ids.append(x['employee_id'])	
		
			sr = 1
			ptotal = 0
			for guard in employee_obj.browse(employee_ids):
				att_ids = attendance_obj.search([('employee_id', '=', guard.id),('post_id', '=', post_id.id),('name', '>=', date_from),('name', '<=', date_to)], order='employee_id')
				atts = att_ids
		
				gatt={'01':'','02':'','03':'','04':'','05':'','06':'','07':'','08':'','09':'','10':'','11':'','12':'','13':'','14':'','15':'','16':'','17':'','18':'','19':'','20':'','21':'','22':'','23':'','24':'','25':'','26':'','27':'','28':'','29':'','30':'','31':''}
				gatt['id']=guard.code	
				gatt['name']=guard.name_related	
				gatt['sr'] = sr
				sr += 1
			
				gtotal = 0			
				for att in atts:
					gatt[att.name[-2:]]=att.action[0].upper()
					if att.action[0].upper() == 'P':
						gtotal += 1
					elif att.action[0].upper() == 'E':
						gtotal += 1
					elif att.action[0].upper() == 'D':
						gtotal += 2
				gatt['total'] = gtotal
				guards.append(gatt)	
				ptotal += gtotal
			total = ptotal
			line=({
					'post_name' : post_id.name, 
					'Guards' : guards,
					'Total' : ptotal,
					})
			line_ids.append(line)	
		res = line_ids
		
		
		
		report =  self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_postsattendance_register')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Register": res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
