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



class ReportWeaponCenterSpecific(models.AbstractModel):
	_name = 'report.sos_uniform.report_weaponcenterspecific'
	_description = 'Specific Center Weapon Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_center_projects(self, center_id):
		project_obj = self.env['sos.project']
		self.env.cr.execute("select distinct project_id from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s"%center_id)
		rec_ids = self.env.cr.dictfetchall()
		
		project_ids = []
		for rec in rec_ids:
			project_ids.append(rec['project_id'])
		projects = project_obj.search([('id','in',project_ids)])
		return projects		
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		res = []
		
		projects = self.get_center_projects(center_id)
		
		if projects:
			for project in projects:
				weapons = self.env['sos.weapon.demand'].search([('project_id', '=', project.id),('center_id', '=', center_id),('date', '>=', date_from),('date','<=', date_to),('state', '<>', 'reject')],order='date,center_id, post_id')
				if weapons:
					res.append({
						'project_name' : project.name,
						'weapons': weapons,
						})
			
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_weaponcenterspecific')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Center" : res or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
