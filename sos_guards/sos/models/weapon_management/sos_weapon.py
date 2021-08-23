import pdb
import time
import math
import re

from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime


class SOSWeapon(models.Model):
	_name = "sos.weapon"
	_inherit = ['mail.thread']
	_description = "Weapon Details"
	_track = {
		}
	
	@api.multi
	@api.depends('date','todate','post_ids')	
	def _get_current_fnc(self):
		for weap in self:			
			weapon_post_rec = self.env['sos.weapon.post'].search([('weapon_id', '=', weap.id)], limit=1, order='fromdate desc')
			if len(weapon_post_rec) > 0:
				weap.current = weapon_post_rec.current
				weap.post_id = weapon_post_rec.post_id.id
				weap.project_id =  weapon_post_rec.post_id.project_id.id
			else:
				weap.current = False
				weap.post_id = False
				weap.project_id = False

	name = fields.Char('Name')
	image = fields.Binary("Photo", attachment=True, help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	center_id = fields.Many2one('sos.center', string='Center',required=False, index=True, readonly=False, track_visibility='onchange')
	project_id = fields.Many2one('sos.project',string = 'Project', compute='_get_current_fnc', store=True,  index=True, track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Last Post', compute='_get_current_fnc', store=True, index=True, required=False, track_visibility='onchange')
	
	weapon_make = fields.Selection([('local','Local'),('foreign','Foreign'),('other','Other')],'Weapon Make', default='local', track_visibility='onchange')
	weapon_type = fields.Selection([('32_bore','32 Bore Pistol'),('30_bore','30 Bore Pistol'),('12_bore','12 Bore Pump Action'),('222_bore','222 Bore Rifle'), \
				('44_mm','44 MM Rifle'),('7_mm','7 MM Rifle'),('8_mm','8 MM Rifle'),('9_mm','9 MM'),('mp_5','MP-5 (Uzi Gun)'),('other','Other')],'Weapon Type', required=True, track_visibility='onchange')
	code = fields.Char('Code ID', index=True,readonly=True,default=lambda self: self.env['ir.sequence'].get('sos.weapon'))
	weapon_lience = fields.Char('Weapon Lience', track_visibility='onchange')
	weapon_condition = fields.Selection([('new','New'),('used','Used')],'Weapon Condition', track_visibility='onchange')
	
	purchase_date = fields.Date('Purchase Date',track_visibility='onchange')
	purchase_value = fields.Integer('Amount',track_visibility='onchange')
	purchased_by = fields.Char('Purchased By', required=False, track_visibility='onchange')
	city = fields.Char('Purchase Location', required=False, track_visibility='onchange')
	
	todate = fields.Date('To Date')
	current = fields.Boolean(compute='_get_current_fnc', store=True,string='Current')
	post_ids = fields.One2many('sos.weapon.post', 'weapon_id', 'Weapon History')
	repair_ids = fields.One2many('sos.weapon.repairing', 'weapon_id', 'Repairing History')
	
	state = fields.Selection([('draft','Draft'),('store','Main Store'),('regional','Regional Store'),('post','At Post'),('repair','Repair'),('out_of_order','Out Of Order')],'Status', default='draft', track_visibility='onchange')
	remarks = fields.Text('Remarks')
	
	@api.multi
	@api.depends('weapon_type','code')	
	def name_get(self):
		result = []
		for rec in self:
			name = rec.weapon_type
			if name == "32_bore":
				name = "32 Bore Pistol"
			elif name == "30_bore":
				name = "30 Bore Pistol"
			elif name == "12_bore":
				name = "12 Bore Pump Action"
			elif name == "222_bore":
				name = "222 Bore Rifle"
			elif name == "44_mm":
				name = "44 MM Rifle"
			elif name == "7_mm":
				name = "7 MM Rifle"
			elif name == "8_mm":
				name = "8 MM Rifle"
			elif name == "9_mm":
				name = "9 MM Rifle"
			elif name == "mp_5":
				name = "MP-5 (Uzi Gun)"
			else:
				name = "other"
			
			if rec.code:
				name = rec.code + ' / '+ name	
			result.append((rec.id, name))
		return result
		
	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = ['|',('code', '=ilike', name + '%'),('weapon_type', operator, name)]			
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		recs = self.search(domain + args, limit=limit)
		return recs.name_get()
		
	@api.model
	def create(self, vals):
		
		name = vals['weapon_type']
		if name == "32_bore":
			vals['name'] = "32 Bore Pistol"
		elif name == "30_bore":
			vals['name'] = "30 Bore Pistol"
		elif name == "12_bore":
			vals['name'] = "12 Bore Pump Action"
		elif name == "222_bore":
			vals['name'] = "222 Bore Rifle"
		elif name == "44_mm":
			vals['name'] = "44 MM Rifle"
		elif name == "7_mm":
			vals['name'] = "7 MM Rifle"
		elif name == "8_mm":
			vals['name'] = "8 MM Rifle"
		elif name == "9_mm":
			vals['name'] = "9 MM Rifle"
		elif name == "mp_5":
			vals['name'] = "MP-5 (Uzi Gun)"
		else:
			vals['name'] = "other"
						  
		result = super(SOSWeapon, self).create(vals)
		return result
	
	

class SOSWeapondPost(models.Model):
	_name = "sos.weapon.post"
	_description = "SOS Weapon Posts"
	_order = 'fromdate desc'
	
	weapon_id = fields.Many2one('sos.weapon', string = 'Weapon',required=True)				
	center_id = fields.Many2one('sos.center',related='weapon_id.center_id',string='Center',store=True)	
	project_id = fields.Many2one('sos.project', string = 'Project', help = 'Project...')
	post_id = fields.Many2one('sos.post',required=True, string = 'Post', help = 'Post...')
	fromdate = fields.Date('From Date',required=True)
	todate = fields.Date('To Date')
	current = fields.Boolean('Current Post')
	remarks = fields.Char('Remarks', size=64)
	to_reason = fields.Selection([('transfer','Transfer'),('terminate','Post Terminated'),('out_of_order','Out Of Order'),('other','Other')],'Reason',help='Select the Reason of To-Date')				
	

class SOSWeapondRepairing(models.Model):
	_name = "sos.weapon.repairing"
	_description = "SOS Weapon Repairing"
	_order = 'id desc'
	
	weapon_id = fields.Many2one('sos.weapon', string = 'Weapon',required=True)				
	code = fields.Char(related="weapon_id.code", store=True)
	weapon_lience =  fields.Char(related="weapon_id.weapon_lience", store=True)
	date = fields.Date('Date',required=True)
	fault = fields.Text('Fault')
	checked_by = fields.Char('Checked By')
	
	
