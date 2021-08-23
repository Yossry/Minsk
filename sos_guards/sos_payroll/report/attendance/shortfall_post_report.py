import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter


class ReportShortFallPost(models.AbstractModel):
	_name = 'report.sos_payroll.report_shortfallpost'
	_description = 'Posts Short Fall Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_posts(self, data):
		post_obj = self.env['sos.post']
		post_ids  = data['post_ids']
		domain =[]
		
		if post_ids:
			post_ids = post_obj.search([('id', 'in', post_ids)])
		
		if not post_ids:
			center_ids = data['center_ids']
			if center_ids:
				domain = [('center_id', 'in', center_ids),('active','=',True)]
				posts_id = post_obj.search(domain)
				post_ids = posts_id
			
		if not post_ids:
			project_ids= data['project_ids']
			if project_ids:
				domain = [('project_id', 'in', project_ids),('active','=',True)]
				posts_id = post_obj.search(domain)
				post_ids = posts_id		
		
		return post_ids

	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		posts = self.get_posts(data['form'])
		
		total_current = 0
		total_shortfall = 0
		total_attendance = 0
		
		line_ids = []
		res = {}
		
		for post in posts:
			result = 0
			guards = 0
			
			guards = post.guards or 0
			self.env.cr.execute("SELECT sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total \
					FROM sos_guard_attendance t where t.post_id = %s and t.name = %s",(post.id,date_from))
			att_dict = self.env.cr.dictfetchall()[0]
			post_att = att_dict['total'] or 0 
			
			result = (guards - post_att)
			if result > 0:
				line=({
					'post' : post.name,
					'center' : post.center_id.name,
					'project' : post.project_id.name,
					'guards' : guards,
					'result' : result,
					'post_att' : post_att,
					})
				line_ids.append(line)
				total_current += guards
				total_shortfall += result
				total_attendance += post_att or 0
		res = line_ids

		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_shortfallpost')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts" : res or False,
			"Total_Att" : total_attendance or 0,
			"Total_Current" : total_current or 0,
			"Total_ShortFall" : total_shortfall or 0,
			"get_date_formate" : self.get_date_formate,
		}
