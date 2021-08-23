import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class PostsTotalAttendance(models.AbstractModel):
	_name = 'report.sos_payroll.report_poststotalattendance'
	_description = 'Posts Total Attendance Report'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	
	@api.multi	
	def get_post_attendance(self,data,post_id):
		date_from = data['date_from']
		date_to = data['date_to']
		total_att = 0
		
		att_ids = self.env['sos.guard.attendance'].search([('post_id','=',post_id),('name','>=',date_from),('name','<=',date_to)])
		for att_id in att_ids:
			if att_id.action == 'present':
				total_att = total_att + 1
			elif att_id.action == 'double':
				total_att = total_att + 2
			elif att_id.action == 'extra':
				total_att = total_att + 1
			elif att_id.action == 'extra_double':
				total_att = total_att + 2
			else:
				total_att = total_att + 0				
		return total_att	

	@api.model
	def _get_report_values(self, docids, data=None):
		
		center_id = data['form']['center_id'] or False
		project_id = data['form']['project_id'] or False
		posts = []
		if center_id:	
			center_id = self.env['sos.center'].search([('id','=',data['form']['center_id'][0])])
			posts = center_id.post_ids
		if project_id:
			project_id = self.env['sos.project'].search([('id','=',data['form']['project_id'][0])])	
			posts = project_id.post_ids	
			
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_poststotalattendance')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Posts' : posts,
			'get_post_attendance' : self.get_post_attendance,
			'get_date_formate' : self.get_date_formate,
		}