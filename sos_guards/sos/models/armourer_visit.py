from odoo import api, fields, models, _
from datetime import datetime


class SOSArmourerVisit(models.Model):
	_name = "sos.armourer.visit"
	_inherit = ['mail.thread']
	_description = "Armourer Visit Detail"

	name = fields.Char('Name')
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, \
		states={'draft': [('readonly', False)]},track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]}, \
		track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=False, track_visibility='onchange')
	city = fields.Char('City', required=True, track_visibility='onchange')
	weapon_type = fields.Char('Weapon Type', required=True, track_visibility='onchange')
	weapon_no = fields.Char('Weapon No.', track_visibility='onchange')
	ammunation = fields.Char('Ammunation', track_visibility='onchange')
	state = fields.Selection([('draft','Draft'),('done','Approved')],'Status',default='draft', track_visibility='onchange')
	remarks = fields.Text('Work')

	@api.multi
	def visit_approved(self):
		for rec in self:
			rec.write({'state':'done'})

