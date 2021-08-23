from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class holidays_validate(models.TransientModel):
	_name = 'hr.holidays.validate'
	_description = 'Holidays Validation'

	@api.model
	def _get_holidays_ids(self):
		context = dict(self._context or {})
		active_ids = context.get('active_ids')
		holiday_ids = self.env['hr.leave'].browse(active_ids)
			
		if any(holiday.state not in ('confirm') for holiday in holiday_ids):
			raise UserError(_("You have selected some records that are not in approvable state. You can select only 'Confirm' records."))
		
		return holiday_ids and holiday_ids.ids or []
	
	holiday_ids = fields.Many2many('hr.leave','hr_holidays_validate_rel','validate_id','holiday_id','Holidays',default=_get_holidays_ids) 

	@api.multi
	def view_holidays(self):		
		return {
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.leave',
			'domain': [('id', 'in', self.holiday_ids.ids),('state', 'in', ['confirm']),],
			'type': 'ir.actions.act_window',
			'target': 'new',
			'nodestroy': True,
		}
	
	@api.multi
	def do_validate(self):
		holiday_ids = self.env['hr.leave'].search([('id', 'in', self.holiday_ids.ids)])
		for holiday in holiday_ids:
			if holiday.current_user_is_approver:
				holiday.action_approve()
				
		return {'type': 'ir.actions.act_window_close'}
		
