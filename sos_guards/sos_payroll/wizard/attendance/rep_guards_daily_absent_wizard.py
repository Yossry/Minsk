import time
import pdb
from odoo import api, fields, models

class SOSGuardsDailyAbsentWizard(models.TransientModel):
	_name = "guards.daily.absent.wizard"
	_description = "Guards Daily Absent Report"
	
	date_from = fields.Date("Date From",default=lambda *a: time.strftime('%Y-%m-01'))
	date_to = fields.Date("Date To",default=lambda *a: time.strftime('%Y-%m-%d'))		
	center_id = fields.Many2one('sos.center', 'Centers')
  
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'guards_daily_absent_report_aeroo',
			'datas': datas,
		}
