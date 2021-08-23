import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class hr_salary_headoffice(models.TransientModel):
	_name = 'hr.salary.headoffice'
	_description = 'Hr Salary Headoffice Employees Report'

	date_from = fields.Date('Date From', required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('Date To', required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])     

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
			'report_name': 'salary_headoffice_aeroo',
			'datas': datas,
		}


