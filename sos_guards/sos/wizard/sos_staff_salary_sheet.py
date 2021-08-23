import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _

class sos_staff_salary_sheet_wizard(models.TransientModel):
	_name = 'sos.staff.salary.sheet.wizard'
	_description = 'Staff Salary Sheet Wizard'

	date_from = fields.Date('Start Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1,day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1,day=31))[:10])
	report_required = fields.Selection([('headoffice','Head Office'),('regional','Regional')], default='headoffice', string='Head / Regional Office')
	segment_wise = fields.Selection([('yes','Yes'),('no','NO')], default='yes', string="Salary Report By Segment",readonly=True)
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos.action_sos_staff_salary_sheet').with_context(landscape=True).report_action(self, data=datas)
