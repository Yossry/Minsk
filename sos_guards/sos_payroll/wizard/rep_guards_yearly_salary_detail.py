import time
from odoo import api, fields, models

class guards_yearly_salary_detail(models.TransientModel):
	_name ='guards.yearly.salary.detail'
	_description = 'Guards Salary Employee By Category Report'

	employee_ids = fields.Many2many('hr.employee', 'guards_payroll_emp_rel', 'payroll_id', 'employee_id', 'Employees', required=True,domain="[('is_guard','=',True),('current','=',True)]")
	date_from = fields.Date('Start Date', required=True,default=lambda *a: time.strftime('%Y-01-01'))
	date_to = fields.Date('End Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))


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
			'report_name': 'guards.salary.detail.byyear',
			'datas': datas,
		}


