import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportShortFallCenter(models.AbstractModel):
	_name = 'report.sos_payroll.report_shortfallcenter'
	_description = 'Centers Shortfall Guards Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	def get_center_attendance(self,data=None):
		date_from = data['date_from']
		self.env.cr.execute("SELECT c.name as name, c.id as id, \
			sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total \
			FROM sos_guard_attendance t, sos_center c where t.center_id = c.id and t.name = '%s' group by c.name,c.id"%(date_from))
		
		att_dict = self.env.cr.dictfetchall()
		return att_dict or False
		
	def get_curr_guards(self,data=None,center_id=None):
		self.env.cr.execute("select sum(post.guards) as total from sos_post post, res_partner partner where partner.active is True and post.center_id='%s' and post.partner_id = partner.id"%(center_id))
		guard_dict = self.env.cr.dictfetchall()[0]
		guards = guard_dict['total']
		return guards or 0
		
	@api.model
	def _get_report_values(self, docids, data=None):
		
		total_current = 0
		total_attendance = 0
		total_shortfall = 0 
		total_extra = 0
		
		center_atts = self. get_center_attendance(data['form'])
		if center_atts:
			for center_att in center_atts:
				shortfall = 0
				extra = 0
				curr_guards = self.get_curr_guards(data['form'],center_att['id'])
				aa = curr_guards - center_att['total']
				if aa > 0:
					shortfall = aa
				if aa < 0:
					extra = abs(aa)	 
				center_att['guards'] = curr_guards or 0
				center_att['shortfall'] = shortfall or 0
				center_att['extra'] = extra or 0
				
				total_current += curr_guards
				total_attendance += center_att['total']
				total_shortfall += shortfall or 0 
				total_extra += extra or 0
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_shortfallcenter')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : center_atts or False,
			"Total_Current" : total_current or 0,
			"Total_Att" : total_attendance or 0,
			"Total_ShortFall" : total_shortfall or 0,
			"Total_Extra" : total_extra or 0,
			"get_date_formate" : self.get_date_formate,
		}