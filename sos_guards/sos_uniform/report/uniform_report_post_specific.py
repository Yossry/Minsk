import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ReportUniformPostSpecific(models.AbstractModel):
	_name = 'report.sos_uniform.report_uniformpostspecific'
	_description = 'Specific Post Uniform Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_posts(self,project_id,center_id):
		posts = self.env['sos.post'].search([('project_id', '=', project_id), ('center_id', '=', center_id), ('active', '=', True)],order='name')
		return posts		
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		state = data['form']['state'] and data['form']['state']
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		project_id = data['form']['project_id'] and data['form']['project_id'][0]
		res = []
		
		posts = self.get_posts(project_id,center_id)
		
		if posts:
			for post in posts:
				dom = []
				dom = [('date', '>=', date_from), ('date', '<=', date_to),('post_id', '=', post.id)]
				
				if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
					dom += [('state', '=', state)]
				elif state == 'dispatch_deliver':
					dom += [('state', 'in', ['dispatch','done'])]	
				elif state == 'none_dispatched':
					dom += [('state', 'in', ['open','review','approve'])]
				elif state == 'all':
					dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
					
				demands = self.env['sos.uniform.demand'].search(dom)
				if demands:
					res.append({
						'post_name' : post.name,
						'demands': demands,
						})
			
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_uniformpostspecific')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Post" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
