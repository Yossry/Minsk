import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class SosComplaintSummaryReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_complaintsummary'
	_description = 'Complaint Summary Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		start_date = data['form']['start_date'] and data['form']['start_date']
		end_date = data['form']['end_date'] and data['form']['end_date']
		order_by = data['form']['order_by'] and data['form']['order_by']
		
		if start_date and end_date:
			start_date = start_date + ' 00:00:01'
			end_date = end_date + ' 23:59:59'
		
		filter_list = [('complaint_time','>=',start_date),('complaint_time','<=',end_date)]
		
		if data['form']['project_ids']:
			filter_list.append(('project_id','in',data['form']['project_ids']))
		if data['form']['center_ids']:
			filter_list.append(('center_id','in',data['form']['center_ids']))
		if data['form']['coordinator_ids']:
			filter_list.append(('coordinator_id','in',data['form']['coordinator_ids']))
		if data['form']['state']:
			filter_list.append(('state','=',data['form']['state']))
			
		complaints = self.env['sos.complaint'].search(filter_list, order = order_by)
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_complaintsummary')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Complaints' : complaints or False,
			'get_date_formate' : self.get_date_formate,
		}