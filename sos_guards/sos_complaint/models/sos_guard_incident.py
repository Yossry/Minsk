import pdb
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import time
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID


class sos_guard_incident(models.Model):
	_name = "sos.guard.incident"
	_inherit = ['mail.thread']
	_description = "SOS Guard Incident Form"
	_order = "name desc"

	name = fields.Char('Reference',size=16)
	center_id = fields.Many2one('sos.center','Center',required=True)
	project_id = fields.Many2one('sos.project','Project',required=True)
	post_id = fields.Many2one('sos.post','Post')
	post_city = fields.Many2one('sos.city', 'City')

	incident_date = fields.Datetime('Incident Date',required=True,default=lambda self: datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
	guards = fields.Integer('No. of S/Gs',required=True)			
	guards_type = fields.Selection([('armed','Armed'),('unarmed','Un-Armed')],'Guard Category')
	
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Done')],'State', readonly=True, default='draft',track_visibility='onchange')
	sos_guard_involved = fields.Selection([('yes','Yes'),('no','NO')],'SOS Guard Involved', readonly=False,track_visibility='onchange')
	guard_injury = fields.Selection([('yes','Yes'),('no','NO')],'Any Injury Of Guard', readonly=False,track_visibility='onchange')
	injuried_guards = fields.Integer('How Many Guards Injuried')
	guard_shaheed = fields.Selection([('yes','Yes'),('no','NO')],'Any SOS Guard Shaheed', readonly=False,track_visibility='onchange')
	shaheed_guards = fields.Integer('How Many Guards Shaheed')
	dacoity_fir_status = fields.Selection([('yes','Yes'),('no','NO')],'Dacoity FIR Status', readonly=False,track_visibility='onchange')
	
	guard_life_insurance = fields.Selection([('yes','Yes'),('no','NO')],'Guard Life Insurance', readonly=False,track_visibility='onchange')
	guard_medical_insurance = fields.Selection([('yes','Yes'),('no','NO')],'Guard Medical Insurance', readonly=False,track_visibility='onchange')
	robbery_amount = fields.Integer('Robbery Amount')
	sos_compensation_amount = fields.Integer('SOS Compensation Amount')
	bank_compensation_amount = fields.Integer('BANK Compensation Amount')
	
	coordinator_id = fields.Many2one('hr.employee','Coordinator')
	remarks = fields.Text(string='Remarks', track_visibility='onchange', readonly=False,)
	
	@api.multi
	def action_open(self):
		for rec in self:
			rec.state = 'open'
		return True
	
	@api.multi
	def action_done(self):
		for rec in self:
			rec.state = 'done'
		return True	
	
	@api.model				
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.guard.incident')
		vals.update({
			'name': st_number,
		})
		return super(sos_guard_incident, self).create(vals)