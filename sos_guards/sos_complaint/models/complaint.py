import pdb
import datetime
import time
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID

class sos_complaint_category(models.Model):
	_name = "sos.complaint.category"
	_description = "Complaint Category"
	
	@api.multi
	def name_get(self):
		result = []
		for complaint in self:
			name = complaint.name
			if complaint.parent_id:
				name = complaint.parent_id[1]+' / '+name
			result.append((complaint.id, name))
		return result
	
	@api.one
	def _name_get_fnc(self):
		res = self.name_get()
		return dict(res)

	
	name = fields.Char("Category", size=64, required=True)
	complete_name =  fields.Char(compute='_name_get_fnc',string='Name')
	parent_id =  fields.Many2one('sos.complaint.category', 'Parent Category', index=True)
	child_ids =  fields.One2many('sos.complaint.category', 'parent_id', 'Child Categories')
	complaint_ids =  fields.Many2many('sos.complaint', 'complaint_category_rel', 'category_id', 'complaint_id', 'Complaints')
	
	@api.multi
	def _check_recursion(self):
		level = 100
		while len(self.ids):
			self.env.cr.execute('select distinct parent_id from sos_complaint_category where id IN %s', (tuple(self.ids), ))
			ids = filter(None, map(lambda x:x[0], self.env.cr.fetchall()))
			if not level:
				return False
			level -= 1
		return True

	_constraints = [(_check_recursion, 'Error! You cannot create recursive Categories.', ['parent_id'])]


class sos_complaint(models.Model):
	_name = "sos.complaint"
	_description = "Complaints"
	
	@api.multi
	def _calc_date(self):		
		for complaint in self:
			complaint.complaint_date = complaint.complaint_time[:10]
	
	
	NATURE_TYPE = [
		('absent_guard','Absent of Guard'),
		('appointment_letter','Appointment Letter Required'),
		('advance_salary','Request for advance salary'),
		('arrear_issue','Arrear Issue'),
		('attendance_register','Attendance Register Required'),
		
		('behaviour_guard','Complaint Against Secuirty Guard Behaviour'),
		('double_guard','Double Duty of Guard'),
		('decoity','Decoity In Branch'),
		('emergency_leave', 'Guard Leave Branch In Emergency'),
		('frequent_rotation_guard','Frequently Rotation of Security Guards'),
		('guard_company_card','Guards Company Card Required'),
		('incomplete_document','Incomplete Documents'),
		('jersey_required','Jersey / Jacket Required'),
		
		('late_guard','Security Guard Late'),
		('labor_court','Labour Court Issues'),
		('less_quantity_ammunition','Less Quantity of Ammunition'),
		
		('metal_detector','Metal Detector Required'),
		('mistakely_fire','Mistakely Fire In Branch'),
		('medical_fitness','Medical Fitness Certificate Required'),
		('monthly_feedback','Monthly Feedback Report'),
		('metal_detector_out_of_order','Metal Detector Out of Order'),
		('new_ammunition','New Ammunitions Required'),
		('nadra_verify','NADRA Verisys Required'),
		
		('overstay_guard','Guard OverStay in Branch'),
		('overage_guard','OverAge Security Guards'),
		('out_of_order_weapon','Weapon Out of Order'),
		('pistol_pouch','Pistol Pouch Required'),
		
		('regional_office_response','Regional Office Response Regarding Complaints'),
		('replacement_guard','Security Guard Replacement Required'),
		('rotation_guard','Security Guard Rotation Required'),
		('substandard_guard','Sub Standard Security Guards'),
		('shoes_required','Shoes Required'),
		('supervisor_visit','Supervisor Visit Required'),
		('salary_issue','Salary Issue'),
		('salary_increment_issue','Request For Salary Increment'),
		('supervisor_signature','Supervisor Signature Specimen Required'),
		
		('test_fire','Test Fire Required'),
		('training_required','Guards Training Certificate Required'),
		('test_fire_certificate','Test Fire & Certificate'),
		
		('weapon_replacement','Weapon Replacement Required'),
		('weapon_service','Weapon Service Required'),
		('weapon_theft','Weapon Theft Case In Branch'),
		('weapon_required','Weapon Required'),
		('weapon_fitness','Weapon Fitness Certificate Required'),
		('weapon_authority_letter','Weapon Authority Letter Required'),
		('weapon_license_renewals','Weapon License Renewals Required'),
		('untrained_guard','Untrained Security Guard'),
		('uniform_required','Uniform Required'),
				
		('30_bore_rounds','30 Bore Rounds Required'),
		('12_bore_rounds','12 Bore Rounds Required'),
		('other','Other'),
		]
		
	name =  fields.Char('Reference',size=16)
	complainant = fields.Char('Complainant', size=64,required=True)
	contact_no = fields.Char('Mobile Number',size=16)
	phone_no = fields.Char('Phone Number',size=16)
	email = fields.Char('Email',size=32)

	center_id = fields.Many2one('sos.center','Center',required=True)
	project_id = fields.Many2one('sos.project','Project',required=True)
	post_id = fields.Many2one('sos.post','Post',required=True)

	coordinator_id = fields.Many2one('hr.employee','Coordinator')
	supervisor_id = fields.Many2one('hr.employee','Supervisor')
	employee_id = fields.Many2one('hr.employee','Employee/Guard')

	complaint_date = fields.Date(compute='_calc_date', string='Date', store=True, readonly=True)
		
	complaint_time = fields.Datetime('Complaint Date & Time',required=True,default=fields.Datetime.now)
	category_ids = fields.Many2many('sos.complaint.category', 'complaint_category_rel', 'complaint_id', 'category_id', 'Nature')
	complaint_detail = fields.Text('Complaint Detail')

	action_time = fields.Datetime('Action Date & Time')
	action_detail = fields.Text('Action Detail')

	received_by = fields.Many2one('hr.employee','Received By')
	actioned_by = fields.Many2one('hr.employee','Action Taken By')
	closed_by = fields.Many2one('res.users','Closed By')
		
	state = fields.Selection([('draft','Draft'),('open','Open'),('done','Closed')],'Status', readonly=True, track_visibility='onchange',default='draft')
	source = fields.Selection([('phone','Telephone'),('mail','Email')],'Source',)
	
	complaint_nature =  fields.Selection(NATURE_TYPE, string='Complaint Nature',required=True, readonly=True, states={'draft': [('readonly', False)]})
					
	@api.one	
	def complaint_open(self):
		self.state = 'open'
		if self.contact_no:
			#sms_obj = self.env['decentralized.recovery.sms']
			text = "Dear Valued Customer, Your complaint has been received and shall be resolved shortly."
			res = {
				'template_id' : 2,
				'mobile_to' : self.contact_no,
				'app_id' : False,
				'text' : text,
				'gateway' : 1,
				'project_id' : self.project_id.id or False,
				'post_id' : self.post_id.id or False,
				}
			#sms_obj.create(res) ##Remark By the Sarfraz, Because SMS Module is not Installed yet
		return True
	
	@api.one			
	def complaint_close(self):
		self.state = 'done'
		self.closed_by = self.env.user.id
		if self.contact_no:
			#sms_obj = self.env['decentralized.recovery.sms']
			text = "Dear Valued customer, Your complaint has been resolved. We thank you for your patience."
			res = {
				'template_id' : 2,
				'mobile_to' : self.contact_no,
				'app_id' : False,
				'text' : text,
				'gateway' : 1,
				'project_id' : self.project_id.id or False,
				'post_id' : self.post_id.id or False,
				}
			#sms_obj.create(res)  ##Remark By the Sarfraz, Because SMS Module is not Installed yet
		return True
	
	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.complaint')
		vals.update({
			'name': st_number,
		})	
		return super(sos_complaint, self).create(vals)
	

