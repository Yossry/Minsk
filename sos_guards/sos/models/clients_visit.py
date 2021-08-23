import pdb
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime


class SOSClientsVisit(models.Model):
	_name = "sos.clients.visit"
	_inherit = ['mail.thread']
	_description = "Clients Visit Detail"

	name = fields.Char('Name')
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	person_name = fields.Char('Person Name', required=True, track_visibility='onchange')
	designation = fields.Char('Designation', required=True, track_visibility='onchange')
	contract_no = fields.Char('Contact No.', required=True, track_visibility='onchange')
	type = fields.Selection([('supervisor','Supervisor'),('am','Am'),('rm','RM')],'Visitor Type', track_visibility='onchange')
	point_category_ids = fields.Many2many('sos.discussed.point.category', 'client_point_category_rel', 'client_id', 'point_categ_id', 'Points Tags')
	action_category_ids = fields.Many2many('sos.action.category', 'client_action_category_rel', 'client_id', 'action_categ_id', 'Actions Tags')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee', string = "Visitor", domain=[('is_guard','=',False),('active','=',True)], \
		index= True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('done','Approved')],'Status',default='draft', track_visibility='onchange')
	remarks = fields.Text('Remarks')
	next_visit_date = fields.Date('Next Visit Plan', track_visibility='onchange')
	
	@api.multi
	def visit_approved(self):
		for rec in self:
			rec.write({'state':'done'})
	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.clients.visit')
		vals.update({
			'name': st_number,
		})	
		return super(SOSClientsVisit, self).create(vals)	


class SOSDiscussedPointCategory(models.Model):
	_name = "sos.discussed.point.category"
	_description = "Point Category"

	name = fields.Char("Point Tag", required=True)
	clients_ids = fields.Many2many('sos.clients.visit', 'client_point_category_rel', 'point_categ_id', 'client_id', 'Clients')
	
	_sql_constraints = [
		('name_uniq', 'unique (name)', "Tag name already exists !")
	]


class SOSActionCategory(models.Model):
	_name = "sos.action.category"
	_description = "Action Category"

	name = fields.Char("Action Tag", required=True)
	clients_ids = fields.Many2many('sos.clients.visit', 'client_action_category_rel', 'action_categ_id', 'client_id', 'Clients')

	_sql_constraints = [
            ('name_uniq', 'unique (name)', "Tag name already exists !")
	]


class SOSAppMessage(models.Model):
	_name = 'app.message'
	_description = 'App Messages'

	sender_id = fields.Char('Sender')
	receive_id = fields.Char('Receiver')
	date = fields.Datetime('Date')
	title = fields.Char('Title')
	message = fields.Char('Message')
	type = fields.Selection([('normal','normal'),('urgent','urgent')], string='Type')


