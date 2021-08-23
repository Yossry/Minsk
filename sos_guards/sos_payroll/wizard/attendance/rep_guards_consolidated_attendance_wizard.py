import time
import pdb
from odoo import api, fields, models

class GuardsConsolidatedAttendanceWizard(models.TransientModel):
	_name = "guards.consolidated.attendance.wizard"
	_description = "Guards Consolidated Attendance Report"
	
	date_to = fields.Date("Date",default=lambda *a: time.strftime('%Y-%m-%d'))
	
	
		
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.guard.attendance',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_guards_consolidated_attendance').with_context(landscape=True).report_action(self, data=datas)
