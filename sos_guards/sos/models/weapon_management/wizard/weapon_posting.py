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
	

class weapon_transfer(models.TransientModel):

	_name ='sos.weapon.posting'
	_description = 'Weapon Posting at Required Posts'
			
	project_id =fields.Many2one('sos.project', string = 'Project',required=True)
	post_id = fields.Many2one('sos.post', string = 'Post',required=True)
	center_id = fields.Many2one('sos.center', string = 'Center')
	
	weapon_id = fields.Many2one('sos.weapon', string = 'Weapon')
	fromdate = fields.Date('Posting Date',required=True)
	todate = fields.Date('Transfer Date')
	
	lbl =  fields.Char('Labl', size=256)
	remarks = fields.Char('Remarks', size=64)
	current = fields.Boolean('Current Post')
		
	@api.model	
	def default_get(self,fields):
		ret = super(weapon_transfer,self).default_get(fields)		
		context = dict(self._context or {})
		weapon_id = context.get('active_id',False)
		weapon = self.env['sos.weapon'].browse(weapon_id)
		current_post = weapon.post_id and weapon.post_id.name or False
		current = weapon.current or False
		
		if weapon_id:
			msg = 'This wizard will '
			if weapon.current:
				msg = msg + 'Transfer the ' + weapon.name + ' at the new Post. His Current post is '
				if current_post:
					msg = msg + weapon.post_id.name
				
			else:	
				msg = msg + 'Post the ' + weapon.name + ' at the required Post.'			
			ret['weapon_id'] = weapon_id
			ret['current'] = weapon.current
			ret['center_id'] = weapon.center_id.id			
			ret['lbl'] = msg
		return ret

	@api.multi	
	def weapon_transfer(self):
		
		context = dict(self._context or {})
		weapon_pool = self.env['sos.weapon']
		duty_pool = self.env['sos.weapon.post']
		
		for data in self:
			to_date = False
			
			if data.weapon_id.state == 'draft':
				data.weapon_id.state='post'
			
			if data.weapon_id.center_id.id != data.center_id.id:
				data.weapon_id.center_id = data.center_id.id	
				
			if data.current:
				weapon_post_ids = duty_pool.search([('weapon_id', '=', data.weapon_id.id),('todate', '=', False)], limit=1, order='fromdate desc')
				for weapon_post_id in weapon_post_ids:
				
					if weapon_post_id.fromdate > data.todate:
						raise UserError(_('Are You Mad?')) 						

					weapon_post_id.write({
						'todate': data.todate,
						'to_reason': 'transfer',
						'current': False,
						'remarks': data.remarks or False,
					})
		
			rec_id = duty_pool.sudo().create({
				'project_id': data.project_id.id,
				'center_id': data.center_id.id,
				'post_id': data.post_id.id,
				'current': True,
				'weapon_id': data.weapon_id.id,
				'fromdate': data.fromdate,
				'todate': False
	    	})
	    	
	    	# Remarked because it generating Error
	    	#if rec_id:
	    	#	data.weapon_id.state = 'post'
	    		
		return {'type': 'ir.actions.act_window_close'}
