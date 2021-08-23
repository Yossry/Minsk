import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
from openerp import models, fields, api, _

class employee_profile_wizard(models.TransientModel):
	_name = 'employee.profile.wizard'
	_description = 'Employee Profile Wizard'
	
	company_id = fields.Many2one('res.company', 'Company',required=True,default=lambda self: self.env.user.company_id.id)
	emp_status = fields.Selection([('active','Active'),('inactive','InActive'),('both','Both')],'Employee Status',default='active')
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('hr_ext.report_employee_profile').with_context(landscape=True).report_action(self, data=datas)
		
		
			
