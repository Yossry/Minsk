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



class ReportJacket(models.AbstractModel):
	_name = 'report.sos_uniform.report_jacket'
	_description = 'SOS Jacket Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		jackets = self.env['sos.jacket.demand'].search([('date', '>=', date_from),('date','<=', date_to), ('state', '<>', 'reject')],order='date,center_id, post_id')
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_jacket')
		return  {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Jackets" : jackets or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
