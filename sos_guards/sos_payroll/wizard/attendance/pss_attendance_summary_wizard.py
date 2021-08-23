
import time
import pdb
from odoo import api, fields, models

class PSSAttendanceSummaryWizard(models.TransientModel):
	
	_name = "sos.pss.attendance.summary.wizard"
	_description = "PSS Attendance Summary Report"
	
	date_from = fields.Datetime("Date From",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Datetime("Date To",default=lambda *a: time.strftime('%Y-%m-%d'))
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          

  
		
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.pss.attendance',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_pss_attendance_summary').with_context(landscape=True).report_action(self, data=datas)

		
