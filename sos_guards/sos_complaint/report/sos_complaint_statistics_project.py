import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class SosComplaintStatisticsReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_complaintstatistics'
	_description = 'Complaint Statistics Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
				
		start_date = data['form']['start_date'] and data['form']['start_date']
		end_date = data['form']['end_date'] and data['form']['end_date']
		
		if start_date and end_date:
			start_date = start_date + ' 00:00:01'
			end_date = end_date + ' 23:59:59'
						
		projects = self.env['sos.project'].search([])	
		res = []
		
		total_received = 0
		total_solved = 0
		total_unsolved = 0
		
		
		for project in projects:
					
			self.env.cr.execute("select count(*) as received from sos_complaint where complaint_time >= %s and complaint_time <= %s and project_id = %s",(start_date,end_date,project.id))
			received = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select count(*) as solved from sos_complaint where state= 'done' and complaint_time >= %s and complaint_time <= %s and project_id = %s",(start_date,end_date,project.id))
			solved = self.env.cr.dictfetchall()[0]
			
			self.env.cr.execute("select count(*) as unsolved from sos_complaint where state <> 'done' and complaint_time >= %s and complaint_time <= %s and project_id = %s",(start_date,end_date,project.id))
			unsolved = self.env.cr.dictfetchall()[0]
			
			total_received += int(0 if received['received'] is None else received['received'])
			total_solved += int(0 if solved['solved'] is None else solved['solved'])
			total_unsolved += int(0 if unsolved['unsolved'] is None else unsolved['unsolved'])
			
			res.append({
				'name': project.name,
				'received': received['received'] or '-',
				'solved': solved['solved'] or '-',
				'unsolved': unsolved['unsolved'] or '-',
			
			})
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_complaintstatistics')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Projects' : res or False,
			'Received' : total_received or '-',
			'Solved' : total_solved or '-',
			'Unsolved' : total_unsolved or '-',
			'get_date_formate' : self.get_date_formate,
		}
		
