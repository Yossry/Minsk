import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportGuardsConsolidatedAttendance(models.AbstractModel):
	_name = 'report.sos_payroll.report_guards_consolidatedattendance'
	_description = 'Guards Consoldiated Attendance Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
	
		date_to  = data['form']['date_to'] and data['form']['date_to']
	
		res = []
		projects = self.env['sos.project'].search([])
		centers = self.env['sos.center'].search([])
		
		totals = 0
		presents = 0
		absents= 0
		
		
		for project in projects:
			total_guards =self.env['hr.employee'].search_count([('project_id','=',project.id),('current','=',True),('is_guard','=',True)])
			present_att = self.env['sos.guard.attendance'].search_count([('project_id','=',project.id),('name','=',date_to),('action','in',['present','extra','double','extra_double'])])
			absent_att = self.env['sos.guard.attendance'].search_count([('project_id','=',project.id),('name','=',date_to),('action','=','absent')])

			shortfall_list = []			
			center_count_list = []
			for center in centers:
				shortfall_count = self.env['sos.guard.shortfall'].search_count([('project_id','=',project.id),('name','=',date_to),('center_id','=',center.id)])
				if shortfall_count:				
					shortfall_list.append(center.code + " ("+ str(shortfall_count)+")")					
			
				center_count = 	self.env['hr.employee'].search_count([('project_id','=',project.id),('center_id','=',center.id),('current','=',True),('is_guard','=',True)])
				if center_count:				
					center_count_list.append(center.code +" ("+ str(center_count)+")")
	
			res.append ({
				'name':project.name,
				'coordinator':project.project_coordinator_id.name,
				'guard':total_guards,
				'present':present_att or 0,
				'absent':absent_att or 0,
				'shortfall': ', '.join(shortfall_list),
				'center_guards': ', '.join(center_count_list),
			})
			
			totals += total_guards
			presents += present_att
			absents += absent_att
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_guards_consolidatedattendance')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Projects" : res or False,
			"Totals" : totals or '-',
			"Presents" : presents or '-',
			'Absents' : absents or '-',
			"get_date_formate" : self.get_date_formate,
		}
		
