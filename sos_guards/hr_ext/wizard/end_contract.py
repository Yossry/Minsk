from datetime import datetime
from odoo import models, fields, api 
import pdb
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class employee_set_inactive(models.TransientModel):
	_name = 'hr.contract.end'
	_description = 'Employee De-Activation Wizard'

	def _get_contract(self):
		return self._context.get('end_contract_id', False)

	def _get_employee(self):		
		contract_id = self._context.get('end_contract_id', False)
		if not contract_id:
		    return False
		return self.env['hr.contract'].browse(contract_id).employee_id.id

	contract_id = fields.Many2one('hr.contract','Contract',readonly=True,default=_get_contract)
	employee_id = fields.Many2one('hr.employee','Employee',required=True,readonly=True,default=_get_employee)
	date = fields.Date('Date', required=True,default=datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))
	reason_id = fields.Many2one('hr.employee.termination.reason','Reason', required=True,)
	notes = fields.Text('Notes',)
	
	@api.multi
	def set_employee_inactive(self):
		vals = {
			'name': self.date,
			'employee_id': self.employee_id.id,
			'reason_id': self.reason_id.id,
			'notes': self.notes,
			'terminate_date': self.date,
			'department_id': self.employee_id.department_id.id,
		}

		self.contract_id.setup_pending_close(vals)
		return {
			'type': 'ir.actions.act_window_close',
		}
