import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from openerp import api, models
import pytz, datetime
from dateutil import tz
from openerp import tools
from operator import itemgetter
from dateutil.relativedelta import relativedelta

class ReportPSSAttendance(models.AbstractModel):
	_name = 'report.sos_payroll.report_pssattendance'
	_description = 'PSS Attendance Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		center_ids = data['form']['center_ids'] and data['form']['center_ids']
		line_ids = []
		res = {}
		#date_from  = date_from + " 00:00:01"
		#date_to  = date_to + " 23:59:59"
		
		att_obj = self.env['sos.pss.attendance']
		
		for center_id in center_ids:
			center = self.env['sos.center'].search([('id','=',center_id)]) 
			att_lines = att_obj.suspend_security().search([('device_datetime','>=', date_from),('device_datetime','<=', date_to), ('center_id','=',center_id)],order='pss_id')
			line=({
				'Center' : center.name, 
				'Lines' : att_lines,
				})
			line_ids.append(line)	
		res = line_ids	
			
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_pssattendance')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Att": res or False,
			"get_date_formate" : self.get_date_formate,
		}