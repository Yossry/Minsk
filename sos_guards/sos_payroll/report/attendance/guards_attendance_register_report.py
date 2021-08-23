import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportGuardsAttendanceRegister(models.AbstractModel):
	_name = 'report.sos_payroll.report_guardsattendance_register'
	_description = 'SOS Guard Attendance Regiser Report'
	
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
		
		attendance_obj = self.env['sos.guard.attendance']
		employee_obj = self.env['hr.employee']
		post_obj = self.env['sos.post']
		
		line_ids = []
		res = {}
		total = 0
						
		employee_obj = self.env['hr.employee']
		domain = [('center_id', '=', center_id),('current','=',True)]				
		employee_ids = employee_obj.search(domain)
		
		for employee_id in employee_ids:
			post_ids = []
			posts = []

			self.env.cr.execute("select distinct post_id from sos_guard_attendance where employee_id=%s and name >= %s and name <=  %s",(employee_id.id,date_from,date_to))
			posts_rec = self.env.cr.dictfetchall()

			for x in posts_rec:
				post_ids.append(x['post_id'])	

			sr = 1
			gtotal = 0
			for post in post_obj.browse(post_ids):
				att_ids = attendance_obj.search([('employee_id', '=', employee_id.id),('post_id', '=', post.id),('name', '>=', date_from),('name', '<=', date_to)], order='post_id')
				atts = att_ids
				patt={'01':'','02':'','03':'','04':'','05':'','06':'','07':'','08':'','09':'','10':'','11':'','12':'','13':'','14':'','15':'','16':'','17':'','18':'','19':'','20':'','21':'','22':'','23':'','24':'','25':'','26':'','27':'','28':'','29':'','30':'','31':''}
				patt['id']=post.id	
				patt['name']=post.name
				patt['sr'] = sr
				sr += 1
			
				ptotal = 0
				for att in atts:
					patt[att.name[-2:]]=att.action[0].upper()
					if att.action[0].upper() == 'P':
						ptotal += 1
					elif att.action[0].upper() == 'E':
						ptotal += 1
					elif att.action[0].upper() == 'D':
						ptotal += 2
				patt['total'] = ptotal
				posts.append(patt)	

				gtotal += ptotal
			total = gtotal
			line=({
					'name' : employee_id.name_related,
					'ref' : employee_id.code,
					'post_name' : post.name, 
					'Posts' : posts,
					'Total' : ptotal,
					})
			line_ids.append(line)	
		res = line_ids
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_guardsattendance_register')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Register": res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
