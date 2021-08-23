import pdb
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class sos_weapon_status_wizard(models.TransientModel):
	_name = 'sos.weapon.status.wizard'
	_description = "SOS Weapon Status Wizard"
		
	state = fields.Selection([('draft','Draft'),('store','Main Store'),('regional','Regional Store'),('post','Post'),('repair','Repair'),('out_of_order','Out Of Order')],'Status', default='draft', track_visibility='onchange')
	
	@api.one
	def weapon_status(self):
		## user zahid = 10, aamir=5 Access Only for Zahid
		
		if self.env.user.id in (1,5,10) :
			weapon_id = self.env['sos.weapon'].browse(self._context.get('active_id',False))
			current_status = weapon_id.state
			weapon_id.state = self.state
		else:
			raise UserError(_('You are not Authorized to do this! Please Contact To Mr.Zahid'))			
		return {'type': 'ir.actions.act_window_close'}	 
	
