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



class ReportUniform(models.AbstractModel):
	_name = 'report.sos_uniform.report_uniform'
	_description = 'Uniform Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		state = data['form']['state'] and data['form']['state']
		
		demand_obj = self.env['sos.uniform.demand']

		dom = [('date', '>=', date_from), ('date', '<=', date_to)]
		
		if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
			dom += [('state', '=', state)]
		elif state == 'dispatch_deliver':
			dom += [('state', 'in', ['dispatch','done'])]	
		elif state == 'none_dispatched':
			dom += [('state', 'in', ['open','review','approve'])]
		elif state == 'all':
			dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]
			
		demands = demand_obj.sudo().search(dom)
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_uniform')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Demands" : demands or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
