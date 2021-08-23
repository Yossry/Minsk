import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
from openerp import api, models
import pytz, datetime
from dateutil import tz
from openerp import tools
from operator import itemgetter


class ReportGuardsWorkingDetail(models.AbstractModel):
	_name = 'report.sos_reports.report_guards_working_detail'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')		
			
	@api.multi
	def render_html(self, data=None):
			
		project_ids = data['form']['project_ids'] or False
		center_ids = data['form']['center_ids'] or False
		post_ids = data['form']['post_ids'] or False
		emps = False
		
		if center_ids:
			centers = False
			centers = self.env['sos.center'].search([('id','in',center_ids)])
			if centers:
				emps = self.env['hr.employee'].search([('center_id','in',centers.ids),('current','=',True),('is_guard','=',True)], order='current_post_id')
		
		if not center_ids and project_ids:
			projects = False
			projects = self.env['sos.project'].search([('id','in',project_ids)])
			if projects:
				emps = self.env['hr.employee'].search([('project_id','in',projects.ids),('current','=',True),('is_guard','=',True)], order='current_post_id')
				
		if not center_ids and project_ids and post_ids:
			posts = False
			posts = self.env['sos.post'].search([('id','in',posts.ids)])
			if posts:
				emps = self.env['hr.employee'].search([('current_post_id','in',posts.ids),('current','=',True),('is_guard','=',True)], order='current_post_id')
		
		
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('sos_reports.report_guards_working_detail')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Recs" : emps or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		return report_obj.render('sos_reports.report_guards_working_detail', docargs)
		
