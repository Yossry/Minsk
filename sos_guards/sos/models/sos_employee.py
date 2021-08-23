import pdb
import re
from datetime import datetime
from odoo import tools
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HRStaff(models.Model):
	_name = "hr.staff"
	_description = "Permanent Staff"

	imsi = fields.Char('IMSI', size=32)
	sim_no = fields.Char('Mobile Number', size=16)
	extension_no = fields.Char('Extension', size=5)
	emp_cv = fields.Boolean('CV')
	emp_exp_certificate = fields.Boolean('Experience Certificates')
	emp_photographs = fields.Boolean('Photos')
	emp_form = fields.Boolean('Employee Form')
	segment_id = fields.Many2one('hr.segmentation', string='Segment')
	sub_segment_id = fields.Many2one('hr.sub.segmentation', string='Sub Segment')
	

class EmployeePhoto(models.Model):
	_name = "hr.employee.photo"
	_description = "HR Employee Photo"

	image = fields.Binary("Photo", help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
	to_be_processed = fields.Boolean(default=True)


class hr_employee(models.Model):
	_name ="hr.employee"
	_inherit = 'hr.employee'
	_inherits = {
		'hr.guard': "guard_id",
		'hr.staff': "staff_info_id",
	}
	
	#Recompute Points
	@api.model
	def recompute_points(self,nlimit=100):		
		employees = self.search([('to_be_processed','=',True)],limit=nlimit)
		for employee in employees:
			employee.guard_id._calc_point()
			employee._calc_age()
			employee.to_be_processed = False
	
	
	#Loading Images	
	@api.model
	def recompute_images(self):
		emps = self.search([('to_be_processed','=',True),('analytic_emp_id','=',False)],limit=100)		
		for emp in emps:		
			emp.vehicle_distance = 10
			emp.to_be_processed = False
	
	#Calculating Age
	@api.one
	def _calc_age(self):
		''' This function will automatically calculates the age of particular employee.'''
		if self.birthday:
			start = datetime.strptime(self.birthday, DEFAULT_SERVER_DATE_FORMAT)
			end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),DEFAULT_SERVER_DATE_FORMAT)
			delta = end - start
			years =  (delta.days / 365)
			self.age = years
	
	#name_get Method Override
	@api.multi
	@api.depends('name','code')	
	def name_get(self):
		result = []
		for emp in self:
			name = emp.name
			if emp.code:
				name = emp.code + ' / ' + name
			result.append((emp.id, name))
		return result
	
	#name_search Method OVerrid
	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = ['|',('code', '=ilike', name + '%'),('name', operator, name)]			
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		emps = self.search(domain + args, limit=limit)
		return emps.name_get()
	
	#Compute Docs Lenght
	@api.one
	def _compute_doc_ids(self):
		emp_attachments = self.env['ir.attachment'].search([('res_model', '=', 'hr.employee'), ('res_id', '=', id)])
		return emp_attachments
	
	
	#Calling Guard Rejoining Form
	@api.multi
	def rejoin_guards_button(self):
		rejoin_form = self.env['ir.ui.view'].search([('name','=','rejoin_guards_form_view')])
		return {
			'name': 'Guards Rejoining',
			'type': 'ir.actions.act_window',
			'res_model': 'sos.rejoin.guards',
			'view_type': 'form',
			'view_mode': 'form',
			'target': 'new',
			'domain': '[]',
			#'view_id': 2343,
			'view_id': rejoin_form.id or False,
			'context': {
				'default_employee_id': self.id,
				'default_name': "Rejoining of" +  " " + self.name,
				'default_previous_appointmentdate': self.appointmentdate,
				'default_previous_terminatedate': self.resigdate,
			}
		}							
	
	@api.multi	
	@api.depends('ref_ids','cnic_expiry','street','mobile_phone','work_phone','bank_id','bankacctitle','bankacc','branch','accowner','mothername',
		'birthday','bloodgroup_id','identity','marital','policestation','postoffice','areanazim','wknownperson','unioncouncil','na_no','pa_no','voteno','kin','wifename',
		'childno','boys','girls','policeverification','nadraattest','cniccopy','nadraattestdate','image_medium')
	def _calc_point(self):
		for employee in self:			
			point = 0
			if employee.ref_ids:
				ref_ids_point = max(len(employee.ref_ids)*7,14)					
				point = point + ref_ids_point
			if employee.name:            
				point = point + 1
			if employee.fathername:
				point = point + 1 
			if employee.cnic:
				point = point + 2 
			if employee.cnic_expiry:
				point = point + 2
			if employee.street:
				point = point + 3
			if employee.mobile_phone:
				point = point + 3
			if employee.work_phone:
				point = point + 3 
			if employee.bank_id:
				point = point + 2
			if employee.bankacctitle:
				point = point + 2 
			if employee.bankacc:
				point = point + 2 
			if employee.branch:
				point = point + 1
			if employee.accowner:
				point = point + 2
			if employee.mothername:
				point = point + 2
			if employee.birthday:
				point = point + 3
			if employee.bloodgroup_id:
				point = point + 1
			if employee.identity:
				point = point + 1
			if employee.marital:
				point = point + 1
			if employee.appointmentdate:
				point = point + 1
			if employee.designation_id:
				point = point + 1
			if employee.policestation:
				point = point + 2
			if employee.postoffice:
				point = point + 2
			if employee.areanazim:
				point = point + 2
			if employee.wknownperson:
				point = point + 2
			if employee.unioncouncil:
				point = point + 1
			if employee.na_no:
				point = point + 1
			if employee.pa_no:
				point = point + 1
			if employee.voteno:
				point = point + 1
			if employee.kin:
				point = point + 2
			if employee.wifename:
				point = point + 2
			if employee.childno:
				point = point + 1
			if employee.boys:
				point = point + 1
			if employee.girls:
				point = point + 1
			if employee.policeverification:
				point = point + 3
			if employee.nadraattest:
				point = point + 3
			if employee.cniccopy:
				point = point + 3
			if employee.nadraattestdate:
				point = point + 3
			if employee.guard_contract_id and employee.guard_contract_id.id == 1:
				point = point + 14
			else:
				if employee.joindate:
					point = point + 1
				if employee.unitname:
					point = point + 1
				if employee.armyno:
					point = point + 1
				if employee.lastunit:
					point = point + 1
				if employee.lastcenter:
					point = point + 1
				if employee.lastdesig:
					point = point + 1
				if employee.serviceperiod:
					point = point + 1
				if employee.recordcenter:
					point = point + 1
				if employee.dischargedate:
					point = point + 1
				if employee.rank:
					point = point + 1	
				if employee.trade:
					point = point + 1
				if employee.forcetype:
					point = point + 1
				if employee.prevforces:
					point = point + 1
				if employee.officername:
					point = point + 1	
			
			if employee.image_medium:
				point = point + 7
		
			employee.points = point	
	
	###Cols
	points = fields.Integer(compute='_calc_point', store=True, readonly=True, track_visibility='always', group_operator="avg")
	code = fields.Char('Code', index=True,default=lambda self: self.env['ir.sequence'].get('hr.employee'))
	age = fields.Integer(compute='_calc_age', store=True, readonly=True)
	remarks = fields.Text(string='Remarks')
	is_guard = fields.Boolean(string='Is Guard',default=True)
	guard_id = fields.Many2one('hr.guard', 'Guard Info', required=True, ondelete="cascade", auto_join=True, index=True)
	staff_info_id = fields.Many2one('hr.staff', 'Staff Info', required=True, ondelete="cascade", auto_join=True, index=True)
	
	emp_rf_ids = fields.One2many('employee.rfid', 'employee_id', 'RF IDS')
	rejoin_ids = fields.One2many('sos.rejoin.guards', 'employee_id', 'Re-Joining IDS')
	transfer_ids = fields.One2many('hr.staff.transfer.history', 'employee_id', 'Transfer History')
	status = fields.Selection([('new', 'New-Hire'),('onboarding', 'On-Boarding'),('active', 'Active'),('pending_inactive', 'Pending Deactivation'),('inactive', 'Inactive'),('reactivated', 'Re-Activated'),('terminated', 'Terminated')],default='new',string='Status',readonly=True)

	@api.multi
	def write(self, vals):
		cnc = vals.get('cnic',False)
		if cnc and self.env.user.id not in (1,5,10,90,83,39,125):
			raise UserError(_('You are not Authorized to do this! Please Contact To Mr.Zahid Ashraf.'))
		res = super(hr_employee, self).write(vals)
		return res	
			
	
	#########
	@api.multi		
	def profile_done(self):
		for guard in self:
			if	guard.profile_status == 'draft':
				guard.profile_status = 'done'
			else:
				raise UserError(_("Dear User, First Should be Draft State. Currently in =  %s.") % guard.profile_status)
	#########
	@api.multi		
	def profile_hr_review(self):
		for guard in self:
			if guard.profile_status == 'done':
				guard.profile_status = 'hr_review'
			else:
				raise UserError(_("Dear User, First Should be Done State. Currently in =  %s.") % guard.profile_status)
	#########
	@api.multi		
	def profile_complete(self):
		for guard in self:
			if guard.profile_status == 'hr_review':
				guard.profile_status = 'complete'
			else:
				raise UserError(_("Dear User, First Should be HR Review . Currently in =  %s.") % guard.profile_status)
	
	#########
	@api.multi
	def profile_lock(self):
		for guard in self:
			guard.lock_profile = True
			msg1 = "Profile is locked By " + self.env.user.name
			guard.message_post(body=msg1)

	#########
	@api.multi
	def profile_unlock(self):
		for guard in self:
			guard.lock_profile = False
			msg1 = "Profile is unlocked By " + self.env.user.name
			guard.message_post(body=msg1)


class EmployeeRFID(models.Model):
	_name = "employee.rfid"
	_inherit = ['mail.thread']

	employee_id = fields.Many2one("hr.employee",'Employee',domain=[('is_guard','=',True),('active','=',True)],track_visibility='always')
	rf_id = fields.Char("RF ID",track_visibility='always')		
	state= fields.Selection([('draft','Draft'),('done','Done')],'State',default='draft')
	
	########
	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete the Record which are not in Draft State. Please Shift First in Draft state then delete it.'))
		ret = super(EmployeeRFID, self).unlink()
		return ret
