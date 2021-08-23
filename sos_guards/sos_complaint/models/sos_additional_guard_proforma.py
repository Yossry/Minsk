import pdb
import datetime
import time
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID


class sos_additional_guard_proforma(models.Model):
	_name = "sos.additional.guard.proforma"
	_inherit = ['mail.thread']
	_order = 'id desc'
	_description = "Additional Guard Proforma"
		
	@api.multi
	@api.depends('guards')
	def _calculate_project_strength(self):
		for rec in self:
			rec.project_strength = len(rec.project_id.employee_ids) + rec.guards

	name = fields.Char('Reference',size=16)
	req_date = fields.Date('Request Date',required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	dep_date = fields.Date('Deployment Date')
	date_from = fields.Date('From Date')
	date_to = fields.Date('To Date')
				
	guards = fields.Integer('No. of S/Gs',required=True)
	guards_type = fields.Selection([('armed','Armed'),('unarmed','Un-Armed')],'Guard Category',)
				
	project_strength = fields.Integer(compute='_calculate_project_strength', store=True, string='Project Strength after deployment')
		
	center_id = fields.Many2one('sos.center','Center',required=True)
	project_id = fields.Many2one('sos.project','Project',required=True)
	post_id = fields.Many2one('sos.post','Post')
	post_name = fields.Char('Branch/Post Name',required=False,size=64)
	post_city = fields.Many2one('sos.city', 'City')
	
	
	coordinator_id = fields.Many2one('hr.employee','Coordinator')
	supervisor_id = fields.Many2one('hr.employee','Supervisor')	
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Done')],'State', readonly=True, default='draft',track_visibility='onchange')
	status = fields.Selection([('deployment','Deployment'),('withdraw','WithDraw')],'Status', readonly=False, default='deployment',track_visibility='onchange')
	deployment_category = fields.Selection([('permanent','Permanent'),('temporary','Temporary')],'Deployment Category', readonly=False, default='temporary',track_visibility='onchange',)
		
	employee_ids = fields.One2many('sos.guard.post', 'post_id', 'Guards History')

	@api.multi
	def action_open(self):
		for rec in self:
			rec.state = 'open'
		return True

	@api.multi
	def action_done(self):
		post_obj = self.env['sos.post']
		job_history_obj = self.env['sos.post.jobs']
		
		category = self.deployment_category
		status = self.status
		guards = self.guards
		
		### add no. of guards in sos_post ###
		if category == 'permanent' and status == 'deployment':
			post_id = post_obj.search([('id','=',self.post_id.id)])
			history_guard_id = job_history_obj.search([('post_id','=',self.post_id.id)])
			if history_guard_id:
				history_guard_id = history_guard_id[0]
				history_guard_id.guards +=guards
				post_id.guards +=guards
		
		### substraction no. of guards in sos_post ###	
		if category == 'permanent' and status == 'withdraw':
			post_id = post_obj.search([('id','=',self.post_id.id)])
			history_guard_id = job_history_obj.search([('post_id','=',self.post_id.id)])[0]
			history_guard_id.guards -=guards
			post_id.guards -=guards	
		self.state = 'done'	
		return True

	@api.model				
	def create(self,vals):
		obj_seq = self.env['ir.sequence']			
		st_number = obj_seq.next_by_code('sos.additional.guard.proforma')
		vals.update({
			'name': st_number,
		})
		return super(sos_additional_guard_proforma, self).create(vals)