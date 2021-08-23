import pdb
import datetime
import time
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID


class sos_deployment(models.Model):
	_name = "sos.deployment"
	_order = 'id desc'
	_description = "New Deployments"
		
	
	@api.one
	@api.depends('guards', 'employee_ids')
	def _calculate_project_strength(self):
		self.project_strength = len(self.project_id.employee_ids) + self.guards

	name = fields.Char('Reference',size=16)
	req_date = fields.Date('Request Date',required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	dep_date = fields.Date('Deployment Date')
				
	guards = fields.Integer('No. of S/Gs',required=True)
	guards_type = fields.Selection([('armed','Armed'),('unarmed','Un-Armed')],'Guard Category',)
				
	project_strength = fields.Integer(compute='_calculate_project_strength', store=True, string='Project Strength after deployment')
		
	center_id = fields.Many2one('sos.center','Center',required=True)
	project_id = fields.Many2one('sos.project','Project',required=True)
	post_id = fields.Many2one('sos.post','Post')
	post_name = fields.Char('Branch/Post Name',required=True,size=64)
	post_city = fields.Many2one('sos.city', 'City')

	paidon = fields.Boolean('Paidon')
	salary_rate = fields.Integer('Proposed Salary Rate')
	invoice_rate = fields.Integer('Invoice Rate')

	coordinator_id = fields.Many2one('hr.employee','Coordinator')
	supervisor_id = fields.Many2one('hr.employee','Supervisor')
		
	received_by = fields.Many2one('hr.employee','Received By')
	received_medium = fields.Char('Medium Reference',size=32)
		
	closed_by = fields.Many2one('res.users','Closed By')
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Done')],'Status', readonly=True, default='draft',track_visibility='onchange',)
	employee_ids = fields.One2many('sos.guard.post', 'post_id', 'Guards History')
					
	@api.multi				
	def deployment_open(self):
		post_obj = self.env['sos.post']
		for rec in self:
			Post = post_obj.create({
				'project_id': rec.project_id.id,
				'post_city': rec.post_city.id,
				'paidon': rec.paidon,
				'startdate': rec.dep_date,
				'guardrate': rec.salary_rate if rec.guards_type == 'unarmed' else 0,
				'guardarmedrate': rec.salary_rate if rec.guards_type == 'armed' else 0,
				'center_id': rec.center_id.id,
				'guards': rec.guards,
				'name': rec.post_name,
				'active': True,
			})
				
		rec.state = 'open'
		rec.post_id = Post.id
		Post.partner_id.post_id = Post.id
		return True
	
	@api.multi
	def deployment_done(self):
		for rec in self:		
			rec.state = 'done'
			rec.closed_by = self.env.user.id
	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.deployment')
		vals.update({
			'name': st_number,
		})
		return super(sos_deployment, self).create(vals)