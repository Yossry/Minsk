import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from openerp import api, fields, models, _
from openerp.exceptions import UserError



class ReportDailyStock(models.AbstractModel):
	_name = 'report.sos_uniform.report_dailystock'
	_description = 'Daily Stock Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def get_report_values(self, docids, data=None):

		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_dailystock')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			#"Jackets" : jackets or False,
			"get_date_formate" : self.get_date_formate,
		}
		
		
