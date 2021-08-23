import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class hr_salary_regions(models.TransientModel):
	_name = 'hr.salary.regions'
	_description = 'Hr Salary Regions Employees Report'

	start_date = fields.Date('Start Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	end_date = fields.Date('End Date', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])        

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
			'report_name': 'salary_regions_aeroo',
			'datas': datas,
		}


