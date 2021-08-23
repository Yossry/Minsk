import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import models, fields, api, _

class employee_statement_wizard(models.TransientModel):
	_name = 'employee.statement.wizard'

			
	date_from = fields.Date('Start Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-2,day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	employee_id = fields.Many2one('hr.employee', 'Employee',required=True,default=lambda self: self._context.get('active_id',False) )


	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['employee_id'] = data['form']['employee_id'] or False
		return result

	
	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'hr.employee',
			'form': data
		}		
		return self.env.ref('aarsol_common.employeestatement').report_action(self, data=datas, config=False)
		

