import pdb
import time
import re
from datetime import datetime
from odoo import tools
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError


class GuardFamily(models.Model):
	_name = "guard.family"
	_description = "Guard Family Detail"

	fathername = fields.Char('Father Name')
	mothername = fields.Char('Mother Name')
	kin = fields.Char('Kin', size=32)
	wifename = fields.Char('Wife Name', size=128)
	childno = fields.Integer('No. of Child')
	boys = fields.Integer('No. of Boys')
	girls = fields.Integer('No. of Girls')
	child_ids = fields.One2many('sos.guard.childs', 'guard_id', 'Childs')
	

class GuardPolitical(models.Model):
	_name = "guard.political"
	_description = "Guard Political Detail"

	policestation = fields.Char('Police Station', size=64)
	postoffice = fields.Char('Post Office', size=32)
	areanazim = fields.Char('Area Nazim Name', size=128)
	wknownperson = fields.Char('Well Known Person', size=128)
	unioncouncil = fields.Char('Union Council No', size=16)
	na_no = fields.Char('NA No', size=16)
	pa_no = fields.Char('PA No', size=16)
	voteno = fields.Char('Vote No', size=16)


class GuardDocuments(models.Model):
	_name = "guard.documents"
	_description = "Guard Documents Detail"

	dischargebook = fields.Boolean('Discharge Book')
	educertificate = fields.Boolean('Eductation Certifcates')
	policeverification = fields.Boolean('Police Verification')
	policeattest = fields.Boolean('Send For Police Attestion')
	nadraattest = fields.Boolean('Nadra Attested')
	pensionbook = fields.Boolean('Identity Card Pension Book')
	cniccopy = fields.Boolean('CNIC Copy')
	nadraattestdate = fields.Date('Nadra Attested Date')


class GuardArmy(models.Model):
	_name = "guard.army"
	_description = "Guard Army Detail"
	
	joindate = fields.Date('Guard Joining Date')
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

	
class SOSGuardFingers(models.Model):
	_description = "SOS Guards Finger"
	_name = "sos.guard.fingers"
	
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


class HREmployeeAddress(models.Model):
	_name = "hr.employee.address"
	_description = "Employee Address Detail"

	home_street = fields.Char('Home Street')
	home_street2 = fields.Char('Home Street 2')
	street = fields.Char('Street')
	street2 = fields.Char('Street 2')


class hr_guard(models.Model):
	_name ="hr.guard"
	_description ="Guards"
	_inherits = {
		'guard.family': "family_id",
		'guard.political': "political_id",
		'guard.documents': "documents_id",
		'guard.army': "army_id",
		'hr.employee.address': "employee_address_id",
		'sos.guard.fingers': "finger_id"
	}
	
	@api.model
	def recompute_posts(self,nlimit=100):	
		duty_obj = self.env['sos.guard.post']	
		guards = self.search([('to_be_processed','=',True)],limit=nlimit)		

		for guard in guards:		
			duty_ids = duty_obj.search([('guard_id','=',guard.id),('todate','=',False)])	
			guard.duty_cnt = len(duty_ids)	
			if(len(duty_ids) == 1):
				for duty_id in duty_ids:	
					guard.current = True
					guard.current_post_id = duty_id.post_id.id
					guard.project_id = duty_id.project_id.id				
					duty_id.processed = True
			elif(len(duty_ids) == 0):	
				guard.current = False
				guard.current_post_id = False
				guard.project_id = False

			guard.to_be_processed = False

	@api.multi
	@api.depends('resigdate','appointmentdate','post_ids','post_ids.todate')	
	def _get_current_fnc(self):
		for emp in self:			
			employee = self.env['hr.employee'].search([('guard_id', '=', emp.id)])
			if employee:
				guard_post_rec = self.env['sos.guard.post'].search([('employee_id', '=', employee.id)], limit=1, order='id desc')
				if len(guard_post_rec) > 0:
					emp.current = guard_post_rec.current
					emp.current_post_id = guard_post_rec.post_id.id
					emp.project_id =  guard_post_rec.post_id.project_id.id
					emp.current_post_start_date = guard_post_rec.fromdate
				else:
					emp.current = False
					emp.current_post_id = False
					emp.project_id = False				
			else:
				emp.current = False
				emp.current_post_id = False
				emp.project_id = False


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
	
	cnic = fields.Char(string='CNIC',index=True, track_visibility='onchange')
	cnic_expiry = fields.Date('CNIC Expiry')
	education_id = fields.Many2one('sos.education','Education')
	designation_id = fields.Many2one('sos.designation','Designation', track_visibility='onchange')
	appointmentdate = fields.Date('Appointment Date', readonly =False, required=True,default=lambda *a: str(datetime.now())[:10])
	resigdate = fields.Date('Resignation Date')
		
	bank_id = fields.Many2one('sos.bank','Bank Name',write=['sos.group_bank_account_info'])
	bankacctitle = fields.Char('Account Title', size=64 ,write=['sos.group_bank_account_info'], track_visibility='onchange')
	bankacc = fields.Char('Account No', size=32,  write=['sos.group_bank_account_info'],track_visibility='onchange')
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner',write=['sos.group_bank_account_info'])
	branch =  fields.Char('Branch', size=64,write=['sos.group_bank_account_info'])
	acc_creation_date = fields.Date('Creation Date',write=['sos.group_bank_account_info'])
		
	identity = fields.Char('Identity', size=64)
	height = fields.Char('Height', size=16)
	weight = fields.Char('Weight', size=16)
	bloodgroup_id = fields.Many2one('sos.bloodgroup','Guard Blood Group')
	cast_id = fields.Many2one('sos.cast', 'Cast')
	subcast_id = fields.Many2one('sos.subcast', 'SubCast')
	religion_id = fields.Many2one('sos.religion','Religion')

	basicpay = fields.Integer('Basic Pay')
	dutybonus = fields.Integer('Duty Bouns')
	wpallowance = fields.Integer('Weapon Allowance')
	annualleaves = fields.Integer('Annual Leaves')
		
	current = fields.Boolean(compute='_get_current_fnc', store=True,string='Current')
	current_post_id = fields.Many2one('sos.post',compute='_get_current_fnc', string='Last Post', track_visibility='onchange',store = True)	
	current_post_start_date = fields.Date(string='Post Appointment Date', compute='_get_current_fnc')
	project_id = fields.Many2one('sos.project',compute='_get_current_fnc',string='Project',	store = True)	
	
	employee_id = fields.Many2one('hr.employee','Employee')
	center_id = fields.Many2one('sos.center','Center')
		
	family_id = fields.Many2one('guard.family', 'Guard Family', required=True, ondelete='cascade', auto_join=True)	
	political_id = fields.Many2one('guard.political', 'Guard Political Info', required=True, ondelete='cascade', auto_join=True)
	documents_id = fields.Many2one('guard.documents', 'Guard Documents', required=True, ondelete='cascade', auto_join=True)
	army_id = fields.Many2one('guard.army', 'Guard Army Info', required=True, ondelete='cascade', auto_join=True)
	employee_address_id = fields.Many2one('hr.employee.address', 'Guard Address', required=True, ondelete='cascade', auto_join=True)

	guard_contract_id = fields.Many2one('guards.contract', 'Contract',write=['sos.group_coordinator','sos.group_special'])
	to_be_processed = fields.Boolean(default=False)
	duty_cnt = fields.Integer("Duty Count")
	profile_status = fields.Selection( [('draft','Draft'),('done','Done'), ('hr_review','Hr Review'),('complete','Complete')],'Profile Status',default='draft',track_visibility='onchange')
	finger_id = fields.Many2one('sos.guard.fingers', 'Guard Fingers', required=True, ondelete='cascade', auto_join=True)
	
	ref_ids = fields.One2many('sos.partneraddress', 'guard_id', 'Ref. Contacts')
	post_ids = fields.One2many('sos.guard.post', 'guard_id', 'Job History')
	emp_rf_ids = fields.One2many('employee.rfid', 'employee_id', 'RF IDS')
	rejoin_ids = fields.One2many('sos.rejoin.guards', 'employee_id', 'Re-Joining IDS')
	exit_form = fields.Boolean(string='Exit Form')
	exit_form_id = fields.Many2one('sos.guards.exit.form', 'Exit Form No.')
	lock_profile = fields.Boolean('Lock Profile',help='This Field is Used To Lock the Profile of the Guard to Restrict Attendance Mark.', default=True)
	
	
	_sql_constraints = [
		('cnic_uniq', 'unique(cnic)', 'Duplicate entry of Guard CNIC is not allowed!'),
	]	


class SOSGuardChilds(models.Model):
	_name = "sos.guard.childs"
	_description = "SOS Guard Childs"

	guard_id = fields.Many2one('hr.guard', string = 'Guard')
	name = fields.Char('Child Name', size=32)
	dob = fields.Date('Date of Birth')
	profession = fields.Char('Child Profession', size=32)
	gender = fields.Selection([('male', 'Male'),('female', 'Female')], 'Gender')

	
class guards_contract(models.Model):
	_name = 'guards.contract'
	_description = 'Guards Contract'

	name = fields.Char('Contract Ref', size=64, required=True)
	employee_ids = fields.One2many('hr.employee', 'guard_contract_id' , string = 'Guuards')		
	date_start = fields.Date('Start Date', required=True,defult=lambda *a: time.strftime("%Y-%m-%d"))
	date_end = fields.Date('End Date')
	wage = fields.Selection([
		('armed-post', 'Post Rate for Armed Guards'),
		('unarmed-post', 'Post Rate for Unarmed Guards'),
		('supervisor-post', 'Post Rate for Supervisors'),
		('senior-post', 'Post Rate for Senior Guards'),
		('searcher-post', 'Post Rate for Lady Searcher'),			
		('mujahid-post', 'Post Rate for Mujahid Guards'),			
		('profile', 'Profile Rate of Guard/Employee'),			
		],'Wages', required=True, help="Basic Salary of the employee")
	
	schedule_pay = fields.Selection([
		('monthly', 'Monthly'),
		('quarterly', 'Quarterly'),
		('semi-annually', 'Semi-annually'),
		('annually', 'Annually'),
		('weekly', 'Weekly'),
		('bi-weekly', 'Bi-weekly'),
		('bi-monthly', 'Bi-monthly'),
		], 'Scheduled Pay', index=True, default='monthly')
	analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
	journal_id = fields.Many2one('account.journal', 'Salary Journal')
	notes = fields.Text('Notes')

	@api.one
	@api.constrains('date_start', 'date_end')	
	def _check_dates(self):
		if self.date_start and self.date_end and self.date_start > self.date_end:
			raise ValueError(_('Error! Contract start-date must be less than contract end-date.'))
		return True
			
	
	
