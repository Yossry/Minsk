import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import api, fields, models

class PFEmployeeStatementWizard(models.TransientModel):
	_name = "pf.employee.statement.wizard"
	_description = "PF Employee Statment"
	
	@api.model
	def _get_employee_id(self):
		emp_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
		if emp_id:
			return emp_id.id
		return True
		
	
	### cols	
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True,default=_get_employee_id)
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_provident_fund.report_pf_employee_statement').with_context(landscape=True).report_action(self, data=datas)

