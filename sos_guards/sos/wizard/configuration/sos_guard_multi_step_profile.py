import pdb
import time
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class sos_guard_multi_step_profile(models.TransientModel):
	_name = 'sos.guard.multi.step.profile'
	_description = 'Guard Multi Step Profile'
	
	
	@api.one
	@api.depends('cnic')
	@api.constrains('cnic')
	def _check_cnic(self):
		cnic_com = re.compile('^[0-9+]{5}-[0-9+]{7}-[0-9]{1}$')
		a = cnic_com.search(self.cnic)
		if a:
			return True
		else:	
			raise UserError(_("CNIC Format is Incorrect. Format Should like this 00000-0000000-0"))
		return True
		
		
	##General DATA
	name = fields.Char('Name', required=True)
	father_name = fields.Char('Father Name', required=True)
	mothername = fields.Char('Mother Name')
	cnic = fields.Char(string='CNIC',index=True, track_visibility='onchange', required=True)
	cnic_expiry = fields.Date('CNIC Expiry')
	birthday = fields.Date('Date of Birth')
	is_guard = fields.Boolean(string='Is Guard',default=True)
	employee_id = fields.Many2one('hr.employee', 'Employee')
	
	#Public Information
	street = fields.Char('Street')
	street2 = fields.Char('Steet2')
	work_phone = fields.Char('Phone')
	mobile_phone = fields.Char('Mobile')
	center_id = fields.Many2one('sos.center','Center')
	department_id = fields.Many2one('hr.department','Department', default=29)
	job_id = fields.Many2one('hr.job', 'Job',default=9)
	
	#Personal Information
	bank_id = fields.Many2one('sos.bank','Bank Name')
	bankacctitle = fields.Char('Account Title', size=64, track_visibility='onchange')
	bankacc = fields.Char('Account No', size=32, track_visibility='onchange')
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner')
	branch =  fields.Char('Branch', size=64,)
	acc_creation_date = fields.Date('Creation Date')
	
	home_street = fields.Char('Home Street')
	home_street2 = fields.Char('Home Steet2')
	#education_id = fields.Many2one('hr.education', 'Education')
	bloodgroup_id = fields.Many2one('sos.bloodgroup', 'Guards Blood Group')
	identity = fields.Char('Identity')
	height = fields.Char('Height')
	weight = fields.Char('Weight')
	gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')], default='male')
	marital = fields.Selection([('single', 'Single'),('married', 'Married'),('cohabitant', 'Legal Cohabitant'),('widower', 'Widower'),('divorced', 'Divorced')], string='Marital Status', default='married')
	
	#HR Setting
	basicpay = fields.Integer('Basic Pay')
	dutybonus = fields.Integer('Duty Bouns')
	wpallowance = fields.Integer('Weapon Allowance')
	annualleaves = fields.Integer('Annual Leaves')
	guard_contract_id = fields.Many2one('guards.contract', 'Contract')
	appointmentdate = fields.Date('Appointment Date', readonly =False, required=True,default=lambda *a: str(datetime.now())[:10])
	resigdate = fields.Date('Resignation Date')
	
	#Political Info
	policestation = fields.Char('Police Station', size=64)
	postoffice = fields.Char('Post Office', size=32)
	areanazim = fields.Char('Area Nazim Name', size=128)
	wknownperson = fields.Char('Well Known Person', size=128)
	unioncouncil = fields.Char('Union Council No', size=16)
	na_no = fields.Char('NA No', size=16)
	pa_no = fields.Char('PA No', size=16)
	voteno = fields.Char('Vote No', size=16)
	
	kin = fields.Char('Kin', size=32)
	wifename = fields.Char('Wife Name', size=128)
	childno = fields.Integer('No. of Child')
	boys = fields.Integer('No. of Boys')
	girls = fields.Integer('No. of Girls')
	
	
	#Documents
	dischargebook = fields.Boolean('Discharge Book')
	educertificate = fields.Boolean('Eductation Certifcates')
	policeverification = fields.Boolean('Police Verification')
	policeattest = fields.Boolean('Send For Police Attestion')
	nadraattest = fields.Boolean('Nadra Attested')
	pensionbook = fields.Boolean('Identity Card Pension Book')
	cniccopy = fields.Boolean('CNIC Copy')
	nadraattestdate = fields.Date('Nadra Attested Date')
	
	#Army Info
	joindate = fields.Date('Joining Date')
	unitname = fields.Char('Unit Name', size=32)
	armyno = fields.Char('Army Force No', size=16)
	lastunit = fields.Char('Last Unit', size=32)
	lastcenter = fields.Char('Last Center', size=48)
	lastdesig = fields.Char('Last Designation', size=32)
	serviceperiod = fields.Char('Service Period', size=16)
	recordcenter = fields.Char('Record Center', size=32)		
	dischargedate = fields.Date('Discharge Date')
	rank = fields.Char('Rank', size=16)
	trade = fields.Char('Trade', size=16)
	forcetype = fields.Char('Force Type', size=16)
	prevforces = fields.Char('Prev Forces', size=16)
	officername = fields.Char('Officer Name', size=128)
	
	#References
	ref_name = fields.Char('Ref. Contact Name', size=64, index=1)
	ref_fathername = fields.Char('Ref. Father Name', size=64)
	ref_cnic = fields.Char('Ref. CNIC', size=20, index=1)
	ref_profession = fields.Char('Ref. Profession', size=128)
	ref_street = fields.Char('Ref. Street', size=128)
	ref_street2 = fields.Char('Ref. Street2', size=128)
	ref_city = fields.Many2one('sos.city', 'Ref. City')
	ref_country_id = fields.Many2one('res.country', 'Ref. Country',default=179)
	ref_email = fields.Char('Ref. Email', size=240)
	ref_phone = fields.Char('Ref. Phone', size=64)
	ref_mobile = fields.Char('Ref. Mobile', size=64)
	ref_fax = fields.Char('Ref. Fax', size=64)
	ref_birthdate = fields.Char('Ref. Birthdate', size=64)
	
	
	#Thumbs
	l_thumb = fields.Binary("Left Thumb", attachment=True, help="This field holds the Left Hand Thumb as photo of the employee")
	l_index_finger = fields.Binary("Left Index Finger", attachment=True, help="This field holds the Left Hand Index Finger as photo of the employee")
	l_middle_finger = fields.Binary("Left Middle Finger", attachment=True, help="This field holds the Left Hand Middle Finger as photo of the employee")
	l_ring_finger = fields.Binary("Left Ring Finger", attachment=True, help="This field holds the Left Hand Ring Finger as photo of the employee")
	l_baby_finger = fields.Binary("Left Baby Finger", attachment=True, help="This field holds the Left Hand Baby Finger as photo of the employee")
	
	r_baby_finger = fields.Binary("Right Baby Finger", attachment=True, help="This field holds the Right Hand Baby Finger as photo of the employee")
	r_ring_finger = fields.Binary("Right Ring Finger", attachment=True, help="This field holds the Right Hand Ring Finger as photo of the employee")
	r_middle_finger = fields.Binary("Right Middle Finger", attachment=True, help="This field holds the Right Hand Middle Finger as photo of the employee")
	r_index_finger = fields.Binary("Right Index Finger", attachment=True, help="This field holds the Right Hand Index Finger as photo of the employee")
	r_thumb = fields.Binary("Right Thumb", attachment=True, help="This field holds the Right Hand Thumb as photo of the employee")

	
	
	
	button_value = fields.Integer('B.Value',default=1)
	show_value = fields.Boolean('Show Value')
	
	@api.multi
	def general_info(self):
		self.ensure_one()
		self.button_value = 1
		
		return {
			'type': 'ir.actions.act_window',
			'name': 'Public Information',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			#'target': 'new',
			#'target': '_blank',
			'context': self._context,
		}
			
		
	@api.multi
	def public_info(self):
		for rec in self:
			rec.button_value = 2
			return {
			'type': 'ir.actions.act_window',
			'name': 'Personal Information',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
		
	
	@api.multi
	def personal_info(self):
		for rec in self:
			rec.button_value = 3
			return {
			'type': 'ir.actions.act_window',
			'name': 'Personal Information',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}					
		
	@api.multi
	def hr_setting(self):
		for rec in self:
			rec.button_value = 4
			return {
			'type': 'ir.actions.act_window',
			'name': 'HR Setting',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
		
	@api.multi
	def political_info(self):
		for rec in self:
			rec.button_value = 5
			return {
			'type': 'ir.actions.act_window',
			'name': 'Political Information',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
		
	@api.multi
	def documents_verify(self):
		for rec in self:
			rec.button_value = 6
			return {
			'type': 'ir.actions.act_window',
			'name': 'Document Verification',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
		
	@api.multi
	def army_info(self):
		for rec in self:
			rec.button_value = 7
			return {
			'type': 'ir.actions.act_window',
			'name': 'Army Information',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
	
	@api.multi
	def guard_references(self):
		for rec in self:
			rec.button_value = 8
			return {
			'type': 'ir.actions.act_window',
			'name': 'References',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}
	
	@api.multi
	def guard_thumbs(self):
		for rec in self:
			rec.button_value = 9
			return {
			'type': 'ir.actions.act_window',
			'name': 'Guard Thumbs',
			'res_model': 'sos.guard.multi.step.profile',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [[False, 'form']],
			'res_id': self.id,
			'target': 'inline',
			'context': self._context,
		}																																										
	
	
	@api.multi
	def create_employee(self):
		for rec in self:
			if rec.ref_name:
				ref_vals = {
					'name' : rec.ref_name and rec.ref_name or '',
					'fathername' : rec.ref_fathername and rec.ref_fathername or '',
					'cnic' : rec.ref_cnic and rec.ref_cnic or '',
					'profession' : rec.ref_profession and rec.ref_profession or '',
					'street': rec.ref_street and rec.ref_street or '',
					'street2' : rec.ref_street2 and rec.ref_street2 or '',
					'city' : rec.ref_city and rec.ref_city.id or False,
					'country_id' : rec.ref_country_id and rec.ref_country_id.id or False,
					'email' : rec.ref_email and rec.ref_email or '',
					'phone' :  rec.ref_phone and rec.ref_phone or '',
					'mobile' : rec.ref_mobile and rec.ref_mobile or '',
					'fax' : rec.ref_fax and rec.ref_fax or '',
					'birthdate' : rec.ref_birthdate and rec.ref_birthdate or '',
					}
			else:
				ref_vals = {}	
				
			vals = {
				'name' : rec.name,
				'fathername' : rec.father_name and rec.father_name or '',
				'mothername' : rec.mothername and rec.mothername or '',
				'cnic' : rec.cnic,
				'cnic_expiry' : rec.cnic_expiry and rec.cnic_expiry or '',
				'birthday' : rec.birthday and rec.birthday or '',
				#'current' : True,
				'street' : rec.street,
				'is_guard' : True,
				'work_phone' : rec.work_phone and rec.work_phone or '',
				'mobile_phone' : rec.mobile_phone and rec.mobile_phone or '',
				'center_id' : rec.center_id and rec.center_id.id or False,
				'department_id' : rec.department_id and rec.department_id.id or False,
				'job_id' : rec.job_id and rec.job_id.id or False,
				'bank_id' : rec.bank_id and rec.bank_id.id or False,
				'bankacctitle' : rec.bankacctitle and rec.bankacctitle or '',
				'bankacc' : rec.bankacc and rec.bankacc or '',
				'accowner' : rec.accowner and rec.accowner or '',
				'branch' : rec.branch and rec.branch or '',
				'acc_creation_date' : rec.acc_creation_date and rec.acc_creation_date or '',
				'home_street' : rec.home_street and rec.home_street or '',
				'home_street2' : rec.home_street2 and rec.home_street2 or '',
				'bloodgroup_id' : rec.bloodgroup_id and rec.bloodgroup_id.id or False,
				'identity' : rec.identity and rec.identity or '',
				'height' : rec.height and rec.height or '',
				'weight' :rec.weight and rec.weight or '',
				'gender' : rec.gender and rec.gender or 'male',
				'marital' : rec.marital and rec.marital or 'married',
				'basicpay' : rec.basicpay and rec.basicpay or 0,
				'dutybonus' : rec.dutybonus and rec.dutybonus or 0,
				'wpallowance' : rec.wpallowance and rec.wpallowance or 0,
				'annualleaves' : rec.annualleaves and rec.annualleaves or 0,
				'guard_contract_id' : rec.guard_contract_id and rec.guard_contract_id.id or False,
				'appointmentdate' : rec.appointmentdate and rec.appointmentdate or '',
				'policestation' : rec.policestation and rec.policestation or '',
				'postoffice' : rec.postoffice and rec.postoffice or '',
				'areanazim' : rec.areanazim and rec.areanazim or '',
				'wknownperson' : rec.wknownperson and rec.wknownperson or '',
				'unioncouncil' : rec.unioncouncil and rec.unioncouncil or '',
				'na_no' : rec.na_no and rec.na_no or '',
				'pa_no' : rec.pa_no and rec.pa_no or '',
				'voteno' : rec.voteno and rec.voteno or '',
				'kin' : rec.kin and rec.kin or '',
				'wifename' : rec.wifename and rec.wifename or '',
				'childno' : rec.childno and rec.childno or '',
				'boys' : rec.boys and rec.boys or '',
				'girls' : rec.girls and rec.girls or '',
				'dischargebook' : rec.dischargebook and rec.dischargebook or False,
				'educertificate' : rec.educertificate and rec.educertificate or False,
				'policeverification' : rec.policeverification and rec.policeverification or False,
				'policeattest' : rec.policeattest and rec.policeattest or False,
				'nadraattest' : rec.nadraattest and rec.nadraattest or False,
				'pensionbook' : rec.pensionbook and rec.pensionbook or False,
				'cniccopy' : rec.cniccopy and rec.cniccopy or False,
				'nadraattestdate' : rec.nadraattestdate and rec.nadraattestdate or False,
				'joindate' : rec.joindate and rec.joindate or '',
				'unitname' : rec.unitname and rec.unitname or '',
				'armyno' : rec.armyno and rec.armyno or '',
				'lastunit' : rec.lastunit and rec.lastunit or '',
				'lastcenter' : rec.lastcenter and rec.lastcenter or '',
				'lastdesig' : rec.lastdesig and rec.lastdesig or '',
				'serviceperiod' : rec.serviceperiod and rec.serviceperiod or '',
				'recordcenter' : rec.recordcenter and rec.recordcenter or '',
				'dischargedate' : rec.dischargedate and rec.dischargedate or '',
				'rank' : rec.rank and rec.rank or '',
				'trade' : rec.trade and rec.trade or '',
				'forcetype' : rec.forcetype and rec.forcetype or '',
				'prevforces' : rec.prevforces and rec.prevforces or '',
				'officername' : rec.officername and rec.officername or '',
				'ref_ids' : [(0, 0, ref_vals)],
				
				}
			
			#CREATE THE RECORD
			#pdb.set_trace()
			resp = self.env['hr.employee'].create(vals)
			rec.employee_id = resp.id		
			_logger.info('....... NEW EMPLOYEE IS CREATED, ID IS .. %r...', resp.id)
					
			

	
