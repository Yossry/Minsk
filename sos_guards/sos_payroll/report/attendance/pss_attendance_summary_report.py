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

class ReportPSSAttendanceSummary(models.AbstractModel):
	_name = 'report.sos_payroll.report_pssattendance_summary'
	_description = 'PSS Attendance Summary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		center_ids = data['form']['center_ids'] and data['form']['center_ids']
		center_lines = []
		res = {}
		
		att_obj = self.env['sos.pss.attendance']
		
		for center_id in center_ids:
			line_ids = []
			
			summary_0 = 0
			summary_1 = 0
			summary_2 = 0
			summary_3 = 0
			summary_4 = 0
			summary_5 = 0
			summary_6 = 0
			summary_7 = 0
			summary_8 = 0
			summary_9 = 0
			summary_10 = 0
			summary_other = 0
			total_branch = 0
			
			center = self.env['sos.center'].search([('id','=',center_id)])
			pss_ids = self.env['sos.pss'].search([('center_id', '=', center_id)])
			
			for pss_id in pss_ids:
				att_count = att_obj.suspend_security().search_count([('device_datetime','>=', date_from),('device_datetime','<=', date_to), ('pss_id','=',pss_id.id)])
				adm_count = att_obj.suspend_security().search_count([('device_datetime','>=', date_from),('device_datetime','<=', date_to), ('pss_id','=',pss_id.id),'|', ('create_uid','=',1),('create_uid','=', False)])
				manual_count = att_obj.suspend_security().search_count([('device_datetime','>=', date_from),('device_datetime','<=', date_to), ('pss_id','=',pss_id.id),'|', ('create_uid','!=',1),('create_uid','!=', False)])
				
				pss_line=({
					'pss_name' : pss_id.name,
					'pss_code' : pss_id.code,
					'att' : att_count,
					})
				line_ids.append(pss_line)
				
				if att_count == 0:
					summary_0 += 1
				elif att_count == 1:
					summary_1 += 1
				elif att_count == 2:
					summary_2 += 1
				elif att_count == 3:
					summary_3 += 1
				elif att_count == 4:
					summary_4 += 1
				elif att_count == 5:
					summary_5 += 1
				elif att_count == 6:
					summary_6 += 1
				elif att_count == 7:
					summary_7 += 1
				elif att_count == 8:
					summary_8 += 1
				elif att_count == 9:
					summary_9 += 1
				elif att_count == 10:
					summary_10 += 1
				else:
					summary_other += 1
																
			total_branches = summary_0 + summary_1 + summary_2 + summary_3 + summary_4 + summary_5 + summary_6 + summary_7 + summary_8 + summary_9 + summary_10 + manual_count
			center_line	=({
				'center_name' : center.name,
				'pss_lines' : line_ids,
				'Summary_0' : summary_0,
				'Summary_1' : summary_1,
				'Summary_2' : summary_2,
				'Summary_3' : summary_3,
				'Summary_4' : summary_4,
				'Summary_5' : summary_5,
				'Summary_6' : summary_6,
				'Summary_7' : summary_7,
				'Summary_8' : summary_8,
				'Summary_9' : summary_9,
				'Summary_10' : summary_10,
				'Manual_Count' : manual_count,
				'Total_Branches' : total_branches,
				})
			center_lines.append(center_line)	
		res = center_lines	
			
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_pssattendance_summary')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Att": res or False,
			"get_date_formate" : self.get_date_formate,
		}
	
