import datetime
import time
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp import SUPERUSER_ID
import pdb


class SOSGuestHouseApproval(models.Model):
	_name = "sos.guest.house.approval"
	_inherit = ['mail.thread']
	_description = "Guest House Approval"
	_order = "name desc"

	name = fields.Char('Number')
	requested_by = fields.Many2one('hr.employee','Requested By',track_visibility='onchange')
	
	check_in = fields.Datetime('Check In',track_visibility='onchange')
	check_out = fields.Datetime('Check Out',track_visibility='onchange')
	days = fields.Integer('No. of Days')
	rent_per_day = fields.Float('Approved Rent Rate Per Day')
	total_rent = fields.Float('Total Rent')
	food = fields.Selection([('YES','YES'),('NO','NO')], string='Food', default='NO',track_visibility='onchange')
	food_amount = fields.Float('Food Amount',track_visibility='onchange')
	
	traveler_type = fields.Selection([('SOS Employees','SOS Employees'),('Other Then SOS','Other Then SOS')], string='Guest Type', default='SOS Employees',track_visibility='onchange')
	sos_traveler_name =fields.Many2one('hr.employee','SOS Guest',track_visibility='onchange')
	vistor_name = fields.Char('Other Guest')
	reference = fields.Char('Reference',track_visibility='onchange')
	purpose= fields.Text('Purpose')
	
	guest_house_name = fields.Char('Guest House Name',track_visibility='onchange')
	city = fields.Char('City',track_visibility='onchange')
	state = fields.Selection([('Draft','Draft'),('Coordinator','Coordinator'),('Admin Approval','Admin Approval'),('Audit Approval','Audit Approval'),('Finance Approval','Finance Approval'),('Accounts Approval','Accounts Approval'),('Paid','Paid')],string='Status',default='Draft',track_visibility='onchange')
	total_amount = fields.Float('Total Amount',track_visibility='onchange')

	@api.onchange('days','rent_per_day','food','food_amount')
	def onchange_total_amount(self):
		total_rent = 0
		total_rent = self.days * self.rent_per_day
		self.total_rent = total_rent
		if self.food == "YES":
			total_rent += self.food_amount
		self.total_amount = total_rent	

	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.guest.house.approval')
		vals.update({
			'name': st_number,
		})
		return super(SOSGuestHouseApproval, self).create(vals)
		
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
