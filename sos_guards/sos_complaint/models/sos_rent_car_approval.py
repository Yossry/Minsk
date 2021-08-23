import datetime
import time
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp import SUPERUSER_ID
import pdb


class SOSCarApproval(models.Model):
	_name = "sos.car.approval"
	_inherit = ['mail.thread']
	_description = "Rent A Car Approval"
	_order = "name desc"

	name = fields.Char('Number')
	requested_by = fields.Many2one('hr.employee','Requested By',track_visibility='onchange')
	
	hiring_date = fields.Datetime('Hiring Date & Time',track_visibility='onchange')
	return_date = fields.Datetime('Return Date & Time',track_visibility='onchange')
	fuel_option = fields.Selection([('With Fuel','With Fuel'),('WithOut Fuel','WihtOut Fuel')], string='Fuel Option', default='With Fuel',track_visibility='onchange')
	fuel_amount = fields.Float('Fuel Amount')
	days = fields.Integer('No. of Days')
	rent_per_day = fields.Float('Approved Rent Rate Per Day')
	total_rent = fields.Float('Total Rent')
	
	traveler_type = fields.Selection([('SOS Employees','SOS Employees'),('Other Then SOS','Other Then SOS')], string='Traveler Type', default='SOS Employees',track_visibility='onchange')
	sos_traveler_name =fields.Many2one('hr.employee','SOS Traveler',track_visibility='onchange')
	vistor_name = fields.Char('Other Traveler')
	reference = fields.Char('Reference',track_visibility='onchange')
	purpose= fields.Text('Purpose')
	
	travel_agent = fields.Many2one('sos.travel.agent','Vendor Name',track_visibility='onchange')
	contact = fields.Char('Contact No.',track_visibility='onchange')
	vehicle_type = fields.Char('Vehicle Type',track_visibility='onchange')
	state = fields.Selection([('Draft','Draft'),('Coordinator','Coordinator'),('Admin Approval','Admin Approval'),('Audit Approval','Audit Approval'),('Finance Approval','Finance Approval'),('Accounts Approval','Accounts Approval'),('Paid','Paid')],string='Status',default='Draft',track_visibility='onchange')
	total_amount = fields.Float('Total Amount')
	
	@api.onchange('days','rent_per_day','fuel_option','fuel_amount')
	def onchange_total_amount(self):
		total_rent = 0
		total_rent = self.days * self.rent_per_day
		self.total_rent = total_rent
		if self.fuel_option == "With Fuel":
			total_rent += self.fuel_amount
		self.total_amount = total_rent	

	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.car.approval')
		vals.update({
			'name': st_number,
		})
		return super(SOSCarApproval, self).create(vals)
		
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
