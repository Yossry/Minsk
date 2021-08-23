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
	

class WeaponRepairing(models.TransientModel):

	_name ='weapon.repairing'
	_description = 'Weapon Repairing Wizard'
	
	@api.model
	def _get_weapon_id(self):
		weap_id = self.env['sos.weapon'].browse(self._context.get('active_id',False))
		if weap_id:
			return weap_id.id
		return True	
			
	weapon_id = fields.Many2one('sos.weapon', string = 'Weapon',required=True, default=_get_weapon_id)				
	date = fields.Date('Date',required=True)
	checked_by = fields.Char('Checked By')
	fault = fields.Text('Fault')
		
	

	@api.one	
	def weapon_repairing(self):
		
		weapon_pool = self.env['sos.weapon.repairing']
		
		rec_id = weapon_pool.sudo().create({
			'weapon_id': self.weapon_id.id,
			'code': self.weapon_id.code,
			'weapon_lience': self.weapon_id.weapon_lience,
			'date': self.date,
			'fault': self.fault,
			'checked_by': self.checked_by
    	})
		return {'type': 'ir.actions.act_window_close'}
