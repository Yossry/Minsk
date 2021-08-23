import datetime
import time
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp import SUPERUSER_ID
import pdb


class SOSAirReservation(models.Model):
	_name = "sos.air.reservation"
	_inherit = ['mail.thread']
	_description = "Air Reservation Approval"
	_order = "name desc"

	name = fields.Char('Number')
	requested_by = fields.Many2one('hr.employee','Requested By',track_visibility='onchange')
	booking_date = fields.Date('Booking Date')
	
	departure_date = fields.Datetime('Departure Date',track_visibility='onchange')
	arrival_date = fields.Datetime('Arrival Date',track_visibility='onchange')
	place_from = fields.Char('From',track_visibility='onchange')
	place_to = fields.Char('To',track_visibility='onchange')
	
	mode = fields.Selection([('Domestic','Domestic'),('International','International')], string='Mode', default='Domestic',track_visibility='onchange')
	traveler_type = fields.Selection([('SOS Employees','SOS Employees'),('Other Then SOS','Other Then SOS')], string='Traveler Type', default='SOS Employees',track_visibility='onchange')
	sos_traveler_name =fields.Many2one('hr.employee','SOS Traveler',track_visibility='onchange')
	vistor_name = fields.Char('Other Traveler')
	
	purpose= fields.Text('Purpose')
	
	travel_agent = fields.Many2one('sos.travel.agent','Travel Agent',track_visibility='onchange')
	pnr_no = fields.Char('Ticket No.',track_visibility='onchange')
	flight_time = fields.Datetime('Date & Time of Flight',track_visibility='onchange')
	ticket_mode = fields.Selection([('Return','Return'),('One Way', 'One Way')], string='Ticket Mode', default='Return',track_visibility='onchange')
	fare = fields.Float('Fare',track_visibility='onchange')
	
	ticket_cancellation = fields.Boolean('Cancellation',track_visibility='onchange')
	cancellation_amt = fields.Float('Cancellation Charges')
	state = fields.Selection([('Draft','Draft'),('Coordinator','Coordinator'),('Admin Approval','Admin Approval'),('Audit Approval','Audit Approval'),('Finance Approval','Finance Approval'),('Accounts Approval','Accounts Approval'),('Paid','Paid')],string='Status',default='Draft',track_visibility='onchange')
	
	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.air.reservation')
		vals.update({
			'name': st_number,
		})
		return super(SOSAirReservation, self).create(vals)
		
	@api.multi
	def unlink(self):
		if self.state != 'Draft':
			raise UserError(('You can not delete record which are not in Draft state.'))	
		
	@api.multi
	def Coordinator_Approval(self):
		for rec in self:		
			rec.state = 'Coordinator'
	
	@api.multi
	def Admin_Approval(self):
		for rec in self:		
			rec.state = 'Admin Approval'
	
	@api.multi
	def Audit_Approval(self):
		for rec in self:		
			rec.state = 'Audit Approval'
	
	@api.multi
	def Finance_Approval(self):
		for rec in self:		
			rec.state = 'Finance Approval'
			
	@api.multi
	def Accounts_Approval(self):
		for rec in self:		
			rec.state = 'Accounts Approval'		
	
	@api.multi
	def Action_Paid(self):
		for rec in self:		
			rec.state = 'Paid'
			
	
	@api.onchange('traveler_type')
	def onchange_traveler(self):
		if self.traveler_type == 'SOS Employees':
			self.vistor_name = ''
		elif self.traveler_type == 'Other Then SOS':
			self.sos_traveler_name = False
		else:
			gr = 10


class SOSTravelAgent(models.Model):		
	_name = "sos.travel.agent"
	_description = "Travel Agents"
	
	name = fields.Char('Name')
	code = fields.Char('Code')
	city = fields.Char('City')
	notes = fields.Text('Notes')
