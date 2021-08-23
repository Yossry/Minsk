import pdb
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime


class SOSBlackListedGuards(models.Model):
	_name = "sos.black.list.guards"
	_inherit = ['mail.thread']
	_description = "Black Listed Guards Detail"
	_order = "id"

	name = fields.Char('Guard Name', required=True)
	cnic = fields.Char(string='CNIC',required=True, index=True, track_visibility='onchange')
	father_name = fields.Char('Father Name')
	father_cnic = fields.Char(string='Father CNIC', index=True, track_visibility='onchange')
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	black_list_date = fields.Date('Black Listed Date',track_visibility='onchange')
	black_list_company = fields.Char('Black Lsit By')
	city = fields.Char('City', required=True, track_visibility='onchange')
	criminal_record = fields.Boolean("Any Criminal Record", default=False)
	state = fields.Selection([('draft','Draft'),('done','Approved')],'Status',default='draft', track_visibility='onchange')
	reason = fields.Text('Reason', track_visibility='onchange')
	remarks = fields.Text('Comments')
	
	@api.multi
	def list_approved(self):
		for rec in self:
			rec.write({'state':'done'})

#Guards Rejoining#		
class SOSRejoinGuards(models.Model):
	_name = "sos.rejoin.guards"
	_inherit = ['mail.thread']
	_description = "Rejoined Guards Detail"

	name = fields.Char('Description')
	employee_id = fields.Many2one('hr.employee','Employee')
	previous_appointmentdate = fields.Date('Previous Appointment Date')
	previous_terminatedate = fields.Date('Previous Terminate Date')
	rejoin_date = fields.Date('Rejoin Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'))
	
	@api.multi
	def rejoin_action(self):
		for rec in self:
			msg = "Guard was terminate on " + rec.employee_id.resigdate + ". Rejoined Again on " +  rec.rejoin_date
			rec.employee_id.message_post(body=msg)
			rec.employee_id.appointmentdate = rec.rejoin_date
			rec.employee_id.resigdate = False
			rec.employee_id.current = True
		return {'type': 'ir.actions.act_window_close'}