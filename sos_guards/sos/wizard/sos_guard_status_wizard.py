import pdb
from odoo import tools
from odoo import api, fields, models, _


class sos_guard_status_wizard(models.TransientModel):
	_name = 'sos.guard.status.wizard'
	_description = 'This Will update the Guard Status in Different States'

	status = fields.Selection( [('draft','Draft'),('done','Done'), ('hr_review','Hr Review'), ('mi_review','MI Review'),('complete','Complete')],'Status')
	
	@api.one
	def guard_status(self):
		employee_id = self.env['hr.employee'].browse(self._context.get('active_id',False))
		current_status = employee_id.profile_status
		employee_id.profile_status = self.status
		return {'type': 'ir.actions.act_window_close'}