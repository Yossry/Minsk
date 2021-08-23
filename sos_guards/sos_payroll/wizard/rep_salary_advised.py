import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class salary_advised(models.TransientModel):
	_name = 'salary.advised'
	_description = 'Salary Advised Report'

	date_from = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])      
	report_name = fields.Selection( [('salary_advised_aeroo','Base Post'),('salary_advised_post_aeroo','Post Wise'),('salary_advised_center_aeroo','Center Wise')],'Report',default='salary_advised_post_aeroo')
	

	
	@api.multi
	def print_report(self):
				
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payslip',
			'form' : data
		}
		report_name =  data['report_name']
		if report_name == 'salary_advised_post_aeroo':
			rep = 'sos_payroll.report_salary_advised_post'
			
		if report_name == 'salary_advised_center_aeroo':
			rep = 'sos_payroll.report_salary_advised_center'
			
		if report_name == 'salary_advised_aeroo':
			rep = 'sos_payroll.report_salary_advised_base'		

		return self.env.ref(rep).with_context(landscape=True).report_action(self, data=datas)
		
		
		
