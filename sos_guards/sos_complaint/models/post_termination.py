import pdb
import json
from datetime import datetime, timedelta
from dateutil import relativedelta

from babel.dates import format_datetime, format_date
from odoo import models, fields, api, _
import logging
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp
from odoo import tools, models, SUPERUSER_ID
from odoo.exceptions import UserError


class sos_post_termination(models.Model):
	_name = "sos.post.termination"
	_description = "Post Termination"
	_order = 'name desc'
	_inherit = ['mail.thread']
		
	name = fields.Char('Reference',size=16)
	req_date = fields.Date('Request Date',required=True, readonly=True, default=lambda *a: str(datetime.now())[:10],track_visibility='always')
	terminate_date =  fields.Date('Terminate Date',require=True,track_visibility='onchange')
				
	guards = fields.Integer(compute='_guards_compute', string='No. of S/Gs',store=True)
	project_strength = fields.Integer('Project Strength after Termination',store=True)
		
	center_id = fields.Many2one('sos.center','Center',required=True, track_visibility='onchange')
	project_id = fields.Many2one('sos.project','Project',required=True, track_visibility='onchange')
	post_id = fields.Many2one('sos.post','Post',required=True,  track_visibility='onchange')
		
	coordinator_id = fields.Many2one('hr.employee','Coordinator', track_visibility='onchange')
	supervisor_id = fields.Many2one('hr.employee','Supervisor', track_visibility='onchange')
	officer_id = fields.Many2one('hr.employee','Visit Officer', track_visibility='onchange')
		
	received_by = fields.Many2one('hr.employee','Received By',track_visibility='onchange')
	received_medium = fields.Char('Medium Reference',size=32,track_visibility='onchange')
		
	closed_by = fields.Many2one('res.users','Closed By',track_visibility='onchange')
		
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Done')],'Status', readonly=True, default='draft', track_visibility='onchange',)
	remarks = fields.Text('Remarks')
	
	
	@api.one
	@api.depends('post_id')
	def _guards_compute(self):	
		p_count=0
		post = self.env['sos.post'].search([('id','=',self.post_id.id)])
		self.guards = post.guards
		p_count = self.env['sos.guard.post'].search_count([('project_id', '=', post.project_id.id),('current', '=', True)])
		self.project_strength = p_count - post.guards
		
	@api.one
	def termination_open(self):			
		self.state ='open'
		return True
		
	@api.multi	
	def termination_done(self):
		post = self.env['sos.post'].search([('id','=',self.post_id.id)])
		cur_guards = self.env['sos.guard.post'].search([('post_id','=',self.post_id.id),('current','=', True)])
		cur_weapons = self.env['sos.weapon.post'].search([('post_id','=',self.post_id.id),('current','=', True)])
		if cur_guards:
			for guard in cur_guards:
				guard.current= False
				guard.todate= self.terminate_date
				guard.employee_id.resigdate = self.terminate_date
		post.enddate = self.terminate_date
		post.active = False
		
		if cur_weapons:
			for weapon in cur_weapons:
				weapon.current = False
				weapon.todate = self.terminate_date
				weapon.weapon_id.state = 'regional'
				weapon.weapon_id.project_id = False
				weapon.weapon_id.post_id = False
		self.state = 'done'
		self.closed_by = self.env.uid
	
	@api.one	
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete record which are not in draft state.'))	
	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.post.termination')
		vals.update({
			'name': st_number,
		})
		return super(sos_post_termination, self).create(vals)