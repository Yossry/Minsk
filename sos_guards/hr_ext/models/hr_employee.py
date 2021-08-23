import time
from datetime import date , datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from dateutil import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.osv import expression
import pdb

def parse_date(td):
	resYear = float(td.days)/365.0                  
	resMonth = (resYear - int(resYear))*365.0/30.0 
	resDays = int((resMonth - int(resMonth))*30)
	resYear = int(resYear)
	resMonth = int(resMonth)
	return (resYear and (str(resYear) + "Y ") or "") + (resMonth and (str(resMonth) + "M ") or "") + (resMonth and (str(resDays) + "D") or "")

def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year, month)[1])
	return datetime(year,month,day)

	
class hr_contact_detail(models.Model):
	_name = 'hr.contact.detail'
	_description = 'HR Contract Detail'
	
	c_employee_id = fields.Many2one('hr.employee', 'Work Manager Name')
	c_designation = fields.Char('Designation',related='c_employee_id.department_id.name', help="Department Name, Related Field")
	
	work_address_street = fields.Char("Work Address", help="Working Address")
	work_address_street2 = fields.Char("Work Address 2", help="Working Address 2")
	work_city = fields.Char("City", help="Work City")
	work_country = fields.Many2one('res.country', "Work Country", help="Work Country")
	
	mobile_phone = fields.Char("Work Mobile", help="Work Mobile, Provided by the Company")
	work_phone = fields.Char("Work Phone", help="Office Work Phone, Local Land Line")
	work_extension = fields.Char("Work Extension", help="Work Extension")
	work_email = fields.Char("Work Email", help="Email Address, Official Email Address")
	
	## Emergency Contract ##
	c_name_1 = fields.Char("Name-1")
	c_mobile_1 = fields.Char("Mobile")
	c_phone_1 = fields.Char("Phone")
	c_extension_1 = fields.Char("Extension")
	c_email_1 = fields.Char("Email")
	
	c_name_2 = fields.Char("Name-2")
	c_mobile_2 = fields.Char("Mobile")
	c_phone_2 = fields.Char("Phone")
	c_extension_2 = fields.Char("Extension")
	c_email_2 = fields.Char("Email")
	
	c_home_name = fields.Char("Name")
	c_home_address1 = fields.Char("Home Address")
	c_home_address2 = fields.Char("Home Address2")
	c_home_city = fields.Char("Home City", help="Home City")
	c_home_country = fields.Many2one('res.country', "Home Country", help="Home Country")
	c_home_mobile = fields.Char("Home Mobile")
	c_home_phone = fields.Char("Home Phone")
	c_home_phone2 = fields.Char("Home Phone2")
	c_personal_email = fields.Char("Personal Email")	       


class hr_employee(models.Model):
	_inherit = 'hr.employee'
	_order = 'code'
			
	@api.multi	
	def _compute_age(self):
		for rec in self:			
			if rec.birthday:
				delta = date.today() - rec.birthday
				rec.age = parse_date(delta)
	
	@api.one
	@api.depends('contract_ids')
	def _get_latest_contract(self):
		obj_contract = self.env['hr.contract']
		contract_ids = obj_contract.search([('employee_id', '=', self.id)], order='date_start desc', limit=1)
		if contract_ids:
 			self.contract_id = contract_ids[0]
		else:
			self.contract_id = False
		
	@api.one
	def _get_import_identifier(self):	
		product_identifier = self.env['ir.model.data'].search([('model','=','hr.employee'),('res_id','=',self.id)])
		if product_identifier:
			product_identifier.module = 'EM'
			product_identifier.name = self.code
			self.import_identifier = product_identifier.id
			#self.full_import_identifier = product_identifier.module + '.' + product_identifier.name
		
	@api.multi
	def write(self,vals):
		result = super(hr_employee, self).write(vals)
		if vals.get('code',False):	
			product_identifier = self.env['ir.model.data'].search([('model','=','hr.employee'),('res_id','=',self.id)])
			if product_identifier:
				product_identifier.module = 'EM'
				product_identifier.name = self.code
				self.import_identifier = product_identifier.id
				#self.full_import_identifier = product_identifier.module + '.' + product_identifier.name	
		return result
    	 
	to_be_processed = fields.Boolean()
	address_home_id = fields.Many2one('res.partner', string='Home Address',related='user_id.partner_id')
	birthday = fields.Date('Date of Birth', groups='base.group_user')
	marital = fields.Selection([
		('single', 'Single'),
		('married', 'Married'),
		('cohabitant', 'Legal Cohabitant'),
		('widower', 'Widower'),
		('divorced', 'Divorced')], string='Marital Status', groups="base.group_user", default="single")
	
	#contract_ids = fields.One2many('hr.contract', 'employee_id', 'Contracts')        				
	#contract_id = fields.Many2one('hr.contract', compute='_get_latest_contract', string='Current Contract', help='Latest contract of the employee')	
	#job_id =  fields.Many2one('hr.job',related='contract_id.job_id',string='Job', readonly=True)
	
	job_id =  fields.Many2one('hr.job',string='Job')

	# 'state' is already being used by hr.attendance
	status = fields.Selection([('new', 'New'),('active', 'Active'),('pending_inactive', 'Pending Deactivation'),
		('inactive', 'Inactive'),('terminated','Terminated')],default='new',string='Status',readonly=True,)
	inactive_ids = fields.One2many('hr.employee.termination','employee_id','Deactivation Records',)
	saved_department_id = fields.Many2one('hr.department','Saved Department',)
	
	code = fields.Char('Code')
	country_id = fields.Many2one('res.country', 'Nationality (Country)', groups="base.group_user")
        
	age = fields.Char("Age",compute='_compute_age')
	
	education_id = fields.Many2one('hr.education','Education')
	joining_date = fields.Date('Joining Date')
	dependents_no = fields.Integer("Dependents No.")
		
	birth_place = fields.Char("Birth Place",translate=True)	
	religion = fields.Char('Employee Religion', help="Employee Religion e.g Muslim")
	blood_group = fields.Selection([('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')],'Blood Group')
	work_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time'),('casual','Casual'),('probation','Probation')],'Work Type')
	
	#cnic = fields.Char('National ID', help="National ID Number") #already defined in the hr_guard
	cnic_expiry_date = fields.Date('Expiry Date',help="National ID Card Expiry Date")
	cnic_days_to_expire = fields.Integer(compute='_cnic_days_to_expire', string="Days to Expire", help="Auto Calculated")
	
	vehical_given = fields.Selection([('By Company','By Company'),('Self','Self'),('Rent','Rent'),('Other', 'Other')],'Vehicle')
	vehical_number = fields.Char('Vehicle Number')
	
	auth_valid_from = fields.Date('Authorization Valid From',help="Authorization Valid From")
	auth_valid_to = fields.Date('Authorization Valid To',help="Authorization Valid To")
		
	health_insurance_ids = fields.One2many('hr.health.insurance', 'employee_id', 'Health Insurance')
	insurance_id = fields.Many2one("hr.health.insurance",'Insurance', compute='_get_latest_insurance_policy',help='Latest Insurance Policy of the Employee',store=True,)
	insurance_deduction = fields.Integer(compute='_get_insurance_data', string="Insurance Deduction",)
	medical_insurance_expire_date = fields.Date('Expired On',compute='_get_insurance_data', help="Medical Insurance Expired Date")
	insurance_class = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('VIP', 'VIP'), ('NA', 'N/A')],'Insurance Class',compute='_get_insurance_data')
	
	passport_ids = fields.One2many('hr.passport', 'employee_id', 'Passport Information')
	emp_passport_id = fields.Many2one("hr.passport",'Passport', compute='_get_latest_passport',help='Latest Passport of the Employee',store=True,)
	#passport_id = fields.Char('Passport No', compute='_get_latest_passport',store=True)
	passport_expire_date = fields.Date('P.Expiry Date',compute='_get_passport_data', help="Passport Expiry Date")
	passport_days_to_expire = fields.Integer('P.Days to Expire',compute='_get_passport_data', help="Days to Expire Passport")
	
	contract_date_start = fields.Date('Contract Start Date',related='contract_id.date_start',help="Contract Sart Date in Normal Calendar")
	contract_date_end = fields.Date('Contract End Date',related='contract_id.date_end',help="Contract End Date in Normal Calendar")
	
	#contact_detail_id = fields.Many2one('hr.contact.detail','Contact Detail', auto_join=True)
	experience_ids = fields.One2many('hr.experience', 'employee_id', 'Experience information')
	
	import_identifier = fields.Many2one('ir.model.data','Import Identifier',compute='_get_import_identifier',store=True)
	full_import_identifier = fields.Char('Full Import Identifier',compute='_get_import_identifier',store=True)
	
	contract_type_id = fields.Many2one('hr.contract.type',"Contract Type")
	apply_provident_fund = fields.Boolean('Deduct Provident Fund?', default=False,track_visibility='onchange')
	
	_sql_constraints = [
		('code_uniq', 'unique(code)', 'Duplicate entry of Code is not allowed!'),
	]
	
	@api.onchange('user_id')
	def _onchange_user(self):
		pass
		#if self.user_id:
		#	self.user_id.email = self.work_email
		#	self.user_id.name = self.name
		#	self.user_id.mobile = self.c_manager_work_mobile or self.c_manager_mobile
		#	self.user_id.phone = self.c_manager_work_phone
		

	@api.depends('passport_ids','passport_ids.expiry_date')
	@api.multi
	def _get_latest_passport(self):
		obj_passport = self.env['hr.passport']
		for employee in self:
			passports = obj_passport.search([('employee_id','=',employee.id),], order='issue_date desc',limit=1)
			for passport in passports:
				employee.emp_passport_id = passport.id
				employee.passport_id = passport.passport_number			
	
	@api.multi	
	def _get_passport_data(self):
		for employee in self:
			if employee.emp_passport_id:				
				employee.passport_expire_date = employee.emp_passport_id.expiry_date		
				employee.passport_days_to_expire = employee.emp_passport_id.days_to_expire		
				
	@api.depends('health_insurance_ids','health_insurance_ids.valid_till')
	@api.multi
	def _get_latest_insurance_policy(self):
		obj_insurance = self.env['hr.health.insurance']
		for employee in self:
			insurance_ids = obj_insurance.search([('employee_id','=',employee.id),], order='valid_from')
			if insurance_ids:
				employee.insurance_id = insurance_ids[-1:][0]
			else:
				employee.insurance_id = False
	
	@api.multi	
	def _get_insurance_data(self):
		for employee in self:
			if employee.insurance_id:
				employee.insurance_deduction = employee.insurance_id.salary_deduction
				employee.medical_insurance_expire_date = employee.insurance_id.valid_till
				employee.insurance_class = employee.insurance_id.insurance_class						
					
	@api.multi	
	def _cnic_days_to_expire(self):
		today = date.today()
		for employee in self:
			if employee.cnic_expiry_date:
				start = fields.Date.today()
				end = employee.cnic_expiry_date
				delta = end - start					
				employee.cnic_days_to_expire = delta.days or 0		
				
	@api.multi		
	def state_active(self):
		for employee in self:
			if employee.status == 'pending_inactive':
				department_id = employee.saved_department_id and employee.saved_department_id.id or False
				employee.write({'status': 'active','department_id': department_id,'saved_department_id': False,})
			else:				
				employee.status = 'active'

	@api.multi
	def state_pending_inactive(self):
		for employee in self:
			saved_department_id = employee.department_id and employee.department_id.id or False
			employee.write({'status': 'pending_inactive','saved_department_id': saved_department_id,'department_id': False,})
		
	@api.multi
	def state_inactive(self):
		for employee in self:	
			vals = {'active': False,'status': 'inactive','job_id': False,}
			if employee.status == 'pending_inactive':
				department_id = employee.saved_department_id and employee.saved_department_id.id or False
				vals.update({'department_id': department_id,'saved_department_id': False,})
			employee.write(vals)
					
	@api.multi	
	def name_get(self):
		result = []
		for emp in self:
			name = emp.name if emp.name else ''
			if emp.code:
				name = emp.code + '-' + name
			result.append((emp.id, name))
		return result 

	@api.model	
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:			
			domain = [('name', operator, name)]		
			if name.isdigit():
				domain = ['|',('code', '=ilike', '%' + name + '%')]	+ domain		
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&'] + domain
		emps = self.search(domain + args, limit=limit)
		return emps.name_get()


class hr_passport(models.Model):
	_name = 'hr.passport'
	_description = 'HR Passport'
	_rec_name = 'passport_number'
	
	@api.multi	
	def _passport_days_to_expire(self):
		for passport in self:
			if passport.issue_date and passport.expiry_date:
				start = datetime.strptime(time.strftime(OE_DFORMAT),OE_DFORMAT)				
				end = datetime.strptime(passport.expiry_date, OE_DFORMAT)
				delta = end - start					
				passport.days_to_expire = delta.days or 0			
	
	
	employee_id = fields.Many2one('hr.employee', string = 'Passport ID')
	passport_number = fields.Char("Passport Number",size=32,required=True)
	issue_date = fields.Date("Passport Issue Date", required=True)
	issue_location = fields.Char("Issue Location", size=32)
	passport_type = fields.Selection([('ordinary', 'Ordinary'), ('diplomatic', 'Diplomatic'),('official', 'Official')],'Passport Type', default='ordinary',help="Passport Type")
	expiry_date = fields.Date("Passport Expire Date", required=True)
	days_to_expire = fields.Integer(compute='_passport_days_to_expire', string="Days to Expire", help="Auto Calculated Passport Expiry Days Remaining")
	
	profession = fields.Char("Profession", size=64)
	
	
class hr_health_insurance(models.Model):
	_name = 'hr.health.insurance'
	_description = 'HR Health Insurance'
	_rec_name = 'membership_number'
	
	
	@api.multi
	def name_get(self):
		result = []
		for rec in self:
			name = rec.policy_number
			if rec.membership_number:
				name = rec.membership_number
			result.append((rec.id, name))
		return result 
	
	
	employee_id = fields.Many2one('hr.employee', string = 'Employee')
	company_name = fields.Many2one('hr.health.insurance.company', string = 'Insurance Company', required=True)
	policy_number = fields.Char("Insurence Policy Number", size=32)
	membership_number = fields.Char("Membership Number", size=32)
	insurance_class = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('VIP', 'VIP'), ('NA', 'N/A')],'Insurance Class')
	amount = fields.Integer("Insurance Amount")
	salary_deduction = fields.Integer("Deduction")
	percentage = fields.Float("Percentage")
	valid_from = fields.Date("Valid From", required=True)
	valid_till = fields.Date("Valid Till", required=True)
	benefits_covered = fields.Text("Benefits Covered")
	covered_members = fields.One2many('hr.health.insurance.line', 'policy_id', 'Covered Members')
	
	#def _check_overlapping(self):
	#	obj_policy_ids = self.search([])
	#	for current_policy in obj_policy_ids:
	#		obj_policy_ids.remove(current_policy.id)
	#		data_policy = self.browse(obj_policy_ids)
	#		for old_ac in data_policy:
	#			if old_ac.valid_from <= current_policy.valid_from <= old_ac.valid_till or old_ac.valid_from <= current_policy.valid_till <= old_ac.valid_till:
	#				return False
	#	return True
	
	def _check_duration(self):
		if self.valid_till < self.valid_from:
			return False
		return True

	_constraints = [
		(_check_duration, _('Error! The duration of the Policy is Invalid.'), ['valid_till']),
		#(_check_overlapping, _('Error! You cannot define overlapping Policicies'), ['valid_from', 'valid_till'])
	]
	
class hr_health_insurance_line(models.Model):
	_name = 'hr.health.insurance.line'
	_description = 'HR Health Insurance Line'
	
	@api.multi	
	def _compute_age(self):
		for rec in self:			
			if rec.birthday:
				start = datetime.strptime(rec.birthday,OE_DFORMAT)
				end = datetime.strptime(time.strftime(OE_DFORMAT),OE_DFORMAT)	
				delta = end - start
				rec.age = parse_date(delta)
	
	policy_id = fields.Many2one('hr.health.insurance', string = 'Policy')
	member_name = fields.Char("Member Name",size=64)
	relationship = fields.Selection([('child', 'Son/Daughter'),('parents', 'Father/mother'),('spouse', 'Spouse')], 'Relationship')
	birthday = fields.Date("Birth Date")
	age = fields.Integer("Age",compute='_compute_age')
	
class hr_health_insurance_company(models.Model):
	_name = 'hr.health.insurance.company'
	_description = 'HR Health Insurance Company'
	
	name = fields.Char("Company Name",size=64,translate=True,)
	
class hr_education(models.Model):
	_name = 'hr.education'
	_description = 'HR Education'
	
	name = fields.Char("Name", size=64, required=True,translate=True,)
	code = fields.Char("Code")
	#employee_ids = fields.One2many('hr.employee', 'education_id', string = 'Employee')	
	
 
class hr_experience(models.Model):
	_name = 'hr.experience'
	_description = "HR Experiences"	
	 
	@api.multi	
	def _total_experience_days(self):
		for rec in self:			
			if rec.start_date and rec.end_date:
				delta = rec.start_date - rec.end_date
				rec.total_experience = parse_date(delta)
				
	name = fields.Char("Company Name")
	employee_id = fields.Many2one('hr.employee', string = 'Employee')
	position = fields.Char("Position")
	salary = fields.Float("Salary")
	currency = fields.Char("Currency")
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	total_experience = fields.Char(compute='_total_experience_days', string="Total Experience", help="Auto Calculated")
	reporting_to = fields.Char("Reporting To")
	reason_to_leave = fields.Text("Reason For Leaving")
	responsibilities = fields.Text("Responsibilities")
	
		
	
		
