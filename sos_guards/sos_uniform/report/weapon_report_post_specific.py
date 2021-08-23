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



class ReportWeaponPostSpecific(models.AbstractModel):
	_name = 'report.sos_uniform.report_weaponpostspecific'
	_description = 'Specific Post Weapon Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')	
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		project_id = data['form']['project_id'] and data['form']['project_id'][0]
		res = []
		
		if project_id and center_id:
			weapons = self.env['sos.weapon.demand'].search([('project_id', '=', project_id),('center_id', '=', center_id),('date', '>=', date_from),('date','<=', date_to),('state', '<>', 'reject')],order='date,center_id, post_id')
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_weaponpostspecific')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Demands" : weapons or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
		
