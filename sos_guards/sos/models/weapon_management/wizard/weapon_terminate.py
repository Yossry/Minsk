# -*- coding: utf-8 -*-
import pdb
import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)
	

class weapon_terminate(models.TransientModel):

	_name ='sos.weapon.terminate'
	_description = 'Weapon Terminate From Posts'
			
	
	weapon_id = fields.Many2one('sos.weapon', string = 'Weapon')	
	todate = fields.Date('To Date',required=True)
	lbl =  fields.Char('Labl', size=256)
	remarks = fields.Char('Remarks', size=64)
	to_reason = fields.Selection([('terminate','Post Terminated'),('escape','Escaped')],'Reason',help='Select the Reason of Termination',required=True)

		
	@api.model	
	def default_get(self,fields):
		ret = super(weapon_terminate,self).default_get(fields)		
		context = dict(self._context or {})
		weapon_id = context.get('active_id',False)
		weapon = self.env['sos.weapon'].browse(weapon_id)
		
		if weapon_id:
			msg = 'This wizard will '
			if weapon.current:
				msg = msg + 'Terminate the ' + weapon.name + ' from the Current Post '
			ret['weapon_id'] = weapon_id
			ret['to_reason'] = 'terminate' 	
			ret['lbl'] = msg
		return ret

	@api.multi	
	def weapon_terminate(self):
		
		context = dict(self._context or {})
		weapon_pool = self.env['sos.weapon']
		duty_pool = self.env['sos.weapon.post']
		
		for data in self:
			to_date = False
			
			if data.weapon_id.current:
				weapon_post_ids = duty_pool.search([('weapon_id', '=', data.weapon_id.id),('todate', '=', False)], limit=1, order='fromdate desc')
				for weapon_post_id in weapon_post_ids:
				
					if weapon_post_id.fromdate > data.todate:
						raise UserError(_('Are You Mad?')) 						

					weapon_post_id.write({
						'todate': data.todate,
						'to_reason': 'terminate',
						'current': False,
						'remarks': data.remarks or False,
					})
			data.weapon_id.state = 'regional'
			data.weapon_id.project_id= False
			data.weapon_id.post_id = False
				
		return {'type': 'ir.actions.act_window_close'}
