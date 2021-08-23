import pdb
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SOSGuardPayslipDraftwizard(models.TransientModel):
	_name = 'sos.guard.payslip.draft.wizard'
	_description = 'This will Change the Payslip into Draft State'
	
	@api.model
	def _get_employee_id(self):
		emp_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
		if emp_id:
			return emp_id.id
		return True
	
	@api.model
	def _get_payslip_id(self):
		emp_id = self._context.get('active_id',False)		
		slip_id = self.env['guards.payslip'].search([('employee_id','=',emp_id)], order='id desc', limit=1)
		if slip_id:
			return slip_id.id
		return True		
	
	### cols	
	employee_id = fields.Many2one('hr.employee', 'Employee', required=True,default=_get_employee_id)
	payslip_id = fields.Many2one('guards.payslip', 'Payslip', required=True, default=_get_payslip_id)
	
	
	@api.one
	def payslip_status(self):
		if self.env.user.id == 125:
			move_id = self.payslip_id.move_id or False
			if move_id and self.payslip_id.state == 'done':
				self.env.cr.execute("delete from account_move where id=%s"%(move_id.id))
				self.payslip_id.state='draft'
			else:
				raise UserError(_('No Move Entry For this Payslip'))	
		else:
			raise UserError(_('You are not Authorized to do this! Please Contact To System Administrator'))		
		return {'type': 'ir.actions.act_window_close'}
