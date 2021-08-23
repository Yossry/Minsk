import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
from openerp import models, fields, api, _

class dokkan_staff_salary_sheet_wizard(models.TransientModel):
	_name = 'dokkan.staff.salary.sheet.wizard'

			
	date_from = fields.Date('Start Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1,day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1,day=31))[:10])
	
	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		return result
	
	
	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'hr.payroll',
			'form': data
		}
		
		return self.env.ref('hr_payroll_ext.action_dokkan_staffsalarysheet').with_context(landscape=True).report_action(self, data=datas, config=False)
