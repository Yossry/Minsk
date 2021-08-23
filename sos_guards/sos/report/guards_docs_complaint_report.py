import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo import tools
from operator import itemgetter


class ReportGuardsDocsComplaint(models.AbstractModel):
	_name = 'report.sos.report_guards_docscomplaint'
	_description = 'Guards Docs Complaint Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_projects_posts(self, project_ids,data,active=True):
		date_from = data['date_from']
		date_to = data['date_to']		
		posts_obj = self.env['sos.post']

		dom = [('project_id', 'in', project_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
		post_ids = posts_obj.search(dom)
		return post_ids
		
	def get_posts(self,data):
		p_obj = self.env['sos.post']
		post_ids  = data['post_ids']
		if post_ids:
			post_ids = p_obj.search([('id','in',post_ids)])
		
		if not post_ids:
			center_ids = data['center_ids'] and data['center_ids']
			if center_ids:
				search_period = [('center_id', 'in', center_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
				post_ids = p_obj.search(search_period)

		if not post_ids:
			project_ids= data['project_ids'] and data['project_ids']
			if project_ids:
				post_ids = self._get_projects_posts(project_ids,data,False)	
				
		return post_ids
	
	
	@api.model
	def _get_report_values(self, docids, data=None):
		p_obj = self.env['sos.post']
		order = ''
		guards = False
		
		post_ids = data['form']['post_ids'] and data['form']['post_ids'] or False
		if post_ids:
			post_ids = p_obj.search([('id','in',post_ids)])
			order ='code'
			
		if not post_ids:
			center_ids = data['form']['center_ids'] and data['form']['center_ids']
			if center_ids:
				search_period = [('center_id', 'in', center_ids),('active','=',True)]
				post_ids = p_obj.search(search_period)
				order ='center_id,project_id,current_post_id,code'
				
		if not post_ids:
			project_ids = data['form']['project_ids'] and data['form']['project_ids']
			if project_ids:			
				dom = [('project_id', 'in', project_ids),('active','=',True)]
				post_ids = p_obj.search(dom)
				order ='project_id,center_id,current_post_id,code'
		
		if post_ids:		
			guards = self.env['hr.employee'].search([('current_post_id', 'in', post_ids.ids),('current','=', True),('is_guard','=', True),('notes','!=', False)], order=order)		
						
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_guards_docscomplaint')
		return  {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Guards" : guards or False,
			"get_date_formate" : self.get_date_formate,
		}
