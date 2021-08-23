import time
import pdb
from odoo import tools
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT

from odoo.tools import float_is_zero, float_compare
from dateutil import relativedelta

from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import models, fields, api, _

from lxml import etree
import openerp.addons.decimal_precision as dp

#   CREATE EXTENSION tablefunc;


### Contract Template
#    What is a Badge, A Badge is a little ballon just at menu right.
#    To obtain this result, you might make this steps:
#
#    1- Our model must inherit from: ir.needaction_mixin
#		_inherit = ['ir.needaction_mixin']
#
#	 2- Type the function _needaction_domain_get in our model:
#
#	@api.model
#   def _needaction_domain_get(self):
#        return [('state','in',['draft', 'waiting'])]

def parse_date(td):
	resYear = float(td.days)/365.0                   # get the number of years including the the numbers after the dot
	resMonth = (resYear - int(resYear))*365.0/30.0  # get the number of months, by multiply the number after the dot by 364 and divide by 30.
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

class hr_contract_template(models.Model):
	_name = 'hr.contract.template'
	_description = 'Contract Templates'
	#_inherit = 'ir.needaction_mixin'
	_order = 'date desc'
    
	name = fields.Char('Name',size=64,required=True,readonly=True,states={'draft': [('readonly', False)]},)
	date = fields.Date('Effective Date',required=True,readonly=True,states={'draft': [('readonly', False)]},)
	wage_ids = fields.One2many('hr.contract.template.wage','contract_template_id','Starting Wages', readonly=True,states={'draft': [('readonly', False)]},)
	struct_id = fields.Many2one('hr.payroll.structure','Payroll Structure',readonly=True,states={'draft': [('readonly', False)]},)
	trial_period = fields.Integer('Trial Period',readonly=True,states={'draft': [('readonly', False)]},default=0,help="Length of Trial Period, in days",)
	active = fields.Boolean('Active', default=True)
	state = fields.Selection([('draft', 'Draft'),('approve', 'Approved'),('decline', 'Declined'),],'State',readonly=True,default='draft')
	policy_group_id = fields.Many2one('hr.policy.group','Policy Group',readonly=True,states={'draft': [('readonly', False)]})
	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id,readonly=True,states={'draft': [('readonly', False)]},)
	journal_id = fields.Many2one('account.journal','Salary Journal',readonly=True,states={'draft': [('readonly', False)]},)
	
	
	#@api.model
	#def _needaction_domain_get(self):		
	#	if self.user_has_groups('hr.group_hr_manager'):
	#		domain = [('state', 'in', ['draft'])]
	#		return domain
	#	return False

	@api.one
	def unlink(self):
		if self.state in ['approve', 'decline']:
			raise UserError(_('You may not a delete a record that is not in a Draft state'))
		return super(contract_template, self).unlink()

	@api.one
	def set_to_draft(self):
		self.state = 'draft'
	
	@api.one
	def state_approve(self):
		self.state = 'approve'
	
	@api.one
	def state_decline(self):
		self.state = 'decline'
		


class contract_template_wage(models.Model):
	_name = 'hr.contract.template.wage'
	_description = 'Starting Wages'

	job_id = fields.Many2one('hr.job','Job')
	starting_wage = fields.Integer('Starting Wage',required=True)
	is_default = fields.Boolean('Use as Default',help="Use as default wage")
	contract_template_id = fields.Many2one('hr.contract.template','Contract Settings')
	category_ids = fields.Many2many('hr.employee.category','contract_template_category_rel','contract_template_id','category_id','Tags')
	#company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id)
		
	_sql_constraints = [('unique_job_cinit', 'UNIQUE(job_id, contract_template_id)','A Job Position cannot be referenced more than once in a Contract Settings record.'),]
	
	@api.one
	def unlink(self):
		if contract_template_id.state in ['approve', 'decline']:
			raise UserError(_('You may not a Delete a record that is not in a Draft state'))
		return super(contract_template_wage, self).unlink()


class hr_employee_termination_reason(models.Model):
	_name = 'hr.employee.termination.reason'
	_description = 'Reason for Employment Termination'
  
	name =  fields.Char('Name',size=256,required=True,translate=True)

class hr_employee_termination(models.Model):
	_name = 'hr.employee.termination'
	_description = 'Data Related to Deactivation of Employee'
	_inherit = ['mail.thread']
  
	name = fields.Char('Reference')
	terminate_date = fields.Date('Effective Date',required=True,states={'draft': [('readonly', False)]},)
	reason_id = fields.Many2one('hr.employee.termination.reason','Reason',required=True,states={'draft': [('readonly', False)]},)
	notes = fields.Text('Notes',readonly=True,states={'draft': [('readonly', False)]},)
	employee_id = fields.Many2one('hr.employee','Employee',required=True,)
	department_id = fields.Many2one('hr.department','Department',required=1)
	#saved_department_id = fields.Many2one('hr.department','Department',related='employee_id.saved_department_id',store=True,)
	state = fields.Selection([('draft', 'Draft'),('confirm', 'Confirmed'),('cancel', 'Cancelled'),('done', 'Done'),],'State',readonly=True,default='draft')
        
	_track = {
		'state': {
			'hr_employee_state.mt_alert_state_confirm': (lambda obj: obj['state'] == 'confirm'),
			'hr_employee_state.mt_alert_state_close': (lambda obj: obj['state'] == 'close'),
			'hr_employee_state.mt_alert_state_cancel': (lambda obj: obj['state'] == 'cancel'),
		},
	}

	#@api.model
	#def _needaction_domain_get(self):
	#
	#	users_obj = self.env['res.users']
	#	domain = []
	#
	#	if users_obj.has_group('hr.group_hr_user'):
	#		domain = [('state', 'in', ['draft'])]
	#
	#	if users_obj.has_group('hr.group_hr_manager'):
	#		if len(domain) > 0:
	#			domain = ['|'] + domain + [('state', '=', 'confirm')]
	#		else:
	#			domain = [('state', '=', 'confirm')]
	#
	#	if len(domain) > 0:
	#		return domain
	#		
	#	return False
				

	@api.multi	
	def unlink(self):
		for term in self:
			if term.state not in ['draft']:
				raise UserError(_('Employment termination already in progress. Use the "Cancel" button instead.'))
		    
		return super(hr_employee_termination, self).unlink()

	@api.multi
	def state_confirm(self):
		for term in self:
			term.employee_id.state_pending_inactive()		    
			term.state = 'confirm'
		return True
	
	@api.multi
	def state_cancel(self):
		for term in self:
			term.employee_id.state_active()		    
			for contract in term.employee_id.contract_ids:
				if contract.state == 'pending_close':
					contract.state = 'open'
			term.state = 'cancel'
		return True

	@api.multi
	def state_done(self):
		for term in self:
			today = datetime.now().date()
			effective_date = datetime.strptime(term.name, OE_DFORMAT).date()
			if effective_date > today:
				raise UserError(_('Effective date is still in the future.'))
						
			for contract in term.employee_id.contract_ids:
				if contract.state == 'pending_close':
					contract.contract_close()
			term.employee_id.state_pending_inactive()								
			term.state = 'done'
		return True	

class hr_contract(models.Model):
	_name = 'hr.contract'
	_inherit = 'hr.contract'
	
	@api.one	
	def _condition_trial_period(self):		
		self.condition_trial_period = True if self.trial_date_start else False

	def _get_policy_group(self):
		template = self.get_latest_template()
		return template and template.policy_group_id or self.env['hr.policy.group']

	def _get_struct(self):		
		template = self.get_latest_template()
		return template and template.struct_id or self.env['hr.payroll.structure']
	
	def _get_journal(self):
		template = self.get_latest_template()
		return template and template.journal_id or self.env['account.journal']
	
	def _get_trial_date_start(self):
		template = self.get_latest_template()
		if template and template.trial_period and template.trial_period > 0:
			return datetime.now().strftime(OE_DFORMAT) 
		return False
	
	def _get_trial_date_end(self):
		template = self.get_latest_template()
		if template and template.trial_period and template.trial_period > 0:
			dEnd = datetime.now().date() + timedelta(days=template.trial_period)
			return dEnd.strftime(OE_DFORMAT)
		return False
	
	
	@api.multi
	@api.depends('employee_id.contract_ids')
	def _get_department(self):		
		states = ['pending_close', 'close']
		for contract in self:
			if contract.department_id and contract.state in states:
				contract.department_id = contract.department_id.id
			elif contract.employee_id.department_id:
				contract.department_id = contract.employee_id.department_id.id
		
	@api.one
	def _get_attendance_policy(self):
		self.attendance_policy = self.env.user.company_id.attendance_policy or 'daily'		

	
	attendance_policy = fields.Selection([('none','No Attendance'),('daily','Daily Attendance'),('monthly','Monthly Attendance'),('overtime','Overtime')],
		'Attendance Policy',default=_get_attendance_policy)
	employee_dept_id = fields.Many2one('hr.department',related='employee_id.department_id',string='Default Dept Id')
	policy_group_id = fields.Many2one('hr.policy.group','Policy Group',default=_get_policy_group)
	struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure',default=_get_struct)
	trial_date_start = fields.Date('Trial Start Date',default=_get_trial_date_start)
	trial_date_end = fields.Date('Trial End Date',default=_get_trial_date_end)
	journal_id = fields.Many2one('account.journal', 'Salary Journal',default=_get_journal)
	
	state = fields.Selection([('draft', 'Draft'),('trial', 'Trial'),('trial_ending', 'Trial Period Ending'),('open', 'Open'),
		('contract_ending', 'Ending'),('pending_close', 'Pending Termination'),('close', 'Completed')],
		'State',default='draft',readonly=True,track_visibility='onchange',write=['hr_ext.group_hr_head'])
	# store this field in the database and trigger a change only if the contract is in the right state: we don't want future changes to an employee's department to impact past contracts that have now ended. Increased priority to override hr_simplify.
	department_id = fields.Many2one('hr.department','Department',compute='_get_department',readonly=True,store=True)
	# At contract end this field will hold the job_id, and the job_id field will be set to null so that modules that reference job_id don't include deactivated employees.
	end_job_id = fields.Many2one('hr.job','Job Title',readonly=True,)

	# The following are redefined again to make them editable only in certain states

	employee_id = fields.Many2one('hr.employee',"Employee",required=True,readonly=True,states={'draft': [('readonly', False)]},)
	type_id = fields.Many2one('hr.contract.type',"Contract Type",required=True,readonly=False,states={'draft': [('readonly', False)]},)
	date_start = fields.Date('Start Date',required=True,readonly=True,states={'draft': [('readonly', False)]},)
	wage = fields.Float('Wage',required=True,help="Basic Salary of the employee",track_visibility='onchange')
	condition_trial_period = fields.Boolean(compute='_condition_trial_period', string="Condition Trial Period?")
	company_id = fields.Many2one('res.company',string='Company',related='employee_id.company_id',store=True)

	transportation_allowance = fields.Float('Transportation Allowance',track_visibility='onchange')
	tds = fields.Float('TDS', digits=dp.get_precision('Payroll'), help="Amount for Tax Deduction at Source")
	driver_salay = fields.Boolean('Driver Salary', help="Check this box if you provide allowance for driver")
	medical_insurance = fields.Float('Medical Insurance', digits=dp.get_precision('Payroll'), help="Deduction towards company provided medical insurance")
	voluntary_provident_fund = fields.Float('Voluntary Provident Fund (%)', digits=dp.get_precision('Payroll'), help="VPF is a safe option wherein you can contribute more than the PF ceiling of 12% that has been mandated by the government and VPF computed as percentage(%)")
	house_rent_allowance = fields.Float('House Rent Allowance (%)', digits=dp.get_precision('Payroll'), help="HRA is an allowance given by the employer to the employee for taking care of his rental or accommodation expenses for metro city it is 50% and for non metro 40%. \nHRA computed as percentage(%)",track_visibility='onchange')
	supplementary_allowance = fields.Float('Supplementary Allowance', digits=dp.get_precision('Payroll'),track_visibility='onchange')
	
	segment_id = fields.Many2one(related='employee_id.segment_id',string='Segment',store=True)
	sub_segment_id = fields.Many2one(related='employee_id.sub_segment_id',string="Sub Segment", store=True)
	center_id = fields.Many2one(related='employee_id.center_id', string='Center', store=True)
	
#	@api.multi
#	def _track_subtype(self, init_values):
#		self.ensure_one()
#		if 'state' in init_values and self.state == 'pending':
#			return 'hr_contract.mt_contract_pending'
#		elif 'state' in init_values and self.state == 'trial_ending':
#			return 'hr_contract.mt_alert_trial_ending'
#		elif 'state' in init_values and self.state == 'open':
#			return 'hr_contract.mt_alert_open'
#		elif 'state' in init_values and self.state == 'contract_ending':
#			return 'hr_contract.mt_alert_contract_ending'				
#		elif 'state' in init_values and self.state == 'close':
#			return 'hr_contract.mt_contract_close'
#		elif 'godi_deduction' in init_values:
#			return 'hr_contract.mt_benefits_change'
#		elif 'transportation_allowance' in init_values:
#			return 'hr_contract.mt_benefits_change'
#		elif 'house_rent_allowance' in init_values:
#			return 'hr_contract.mt_benefits_change'
#		elif 'supplementary_allowance' in init_values:
#			return 'hr_contract.mt_benefits_change'
#		elif 'wage' in init_values:
#			return 'hr_contract.mt_benefits_change'
#				
#		return super(hr_contract, self)._track_subtype(init_values)	

	@api.onchange('employee_id')    
	def onchange_employee_id(self):		
		self.employee_dept_id = self.department_id and self.department_id.id or False
		if self.employee_id:
			contracts = self.search_count([('employee_id','=', self.employee_id.id)])
			contracts +=1
			self.name = 'EM.' + str(self.employee_id.code) + '-'+ str(contracts)

		
	@api.one
	def _remove_tags(self, employee_id=None, job_id=None):
		if not employee_id or not job_id:
		    return
		employee = self.env['hr.employee'].browse(employee_id)
		empl_tags = employee.category_ids
		job = self.env['hr.job'].browse(job_id)
		for tag in job.category_ids:
			if tag in empl_tags:
				employee.write({'category_ids': [(3, tag.id)]})

	@api.one
	def _tag_employees(self, employee_id=None, job_id=None):
		if not employee_id or not job_id:
		    return
		employee = self.env['hr.employee'].browse(employee_id)
		empl_tags = employee.category_ids
		job = self.env['hr.job'].browse(job_id)
		for tag in job.category_ids:
			if tag not in empl_tags:
				employee.write({'category_ids': [(4, tag.id)]})

	@api.model
	def create(self, vals):
		res = super(hr_contract, self).create(vals)
		self._tag_employees(vals.get('employee_id', False),vals.get('job_id', False))
		return res

	@api.one
	def write(self, vals):
		prev_job = self.job_id
		new_job = vals.get('job_id', False)

		res = super(hr_contract, self).write(vals)
		
		# Go through each record and delete tags associated with the previous job, then add the tags of the new job.
		if prev_job and new_job and prev_job.id != new_job:
			self._remove_tags(self.employee_id.id,prev_job.id)
			self._tag_employees(self.employee_id.id,new_job)
		return res
	

	@api.onchange('job_id')
	def onchange_job(self):
		#if self.job_id:
		#	self.wage = self._get_wage(job_id=self.job_id)
		if not self.employee_id.job_id.id == self.job_id.id:
			#self.employee_id.job_id = self.job_id.id
			self.env.cr.execute("update hr_employee set job_id=%s where id = %s",(self.job_id.id,self.employee_id.id))	
				
	@api.onchange('trial_date_start')
	def onchange_trial(self):
		template = self.get_latest_template()
		if template and template.trial_period and template.trial_period > 0:
			dStart = datetime.strptime(self.trial_date_start, OE_DFORMAT)
			dEnd = dStart + timedelta(days=template.trial_period)
			self.trial_date_end = dEnd.strftime(OE_DFORMAT)
	
	
	def get_latest_template(self,today_str=False):
		"""Return a record with an effective date before today_str but greater than all others
		"""
		init_obj = self.env['hr.contract.template']
		if not today_str:
			today_str = datetime.now().strftime(OE_DFORMAT)
		dToday = datetime.strptime(today_str, OE_DFORMAT).date()
		template = init_obj.search([('date', '<=', today_str), ('state', '=', 'approve')],order="date desc",limit=1)
		return template
	
	def _get_wage(self,job_id=None):
		wage = 0
		default = 0
		template = self.get_latest_template()
		
		if job_id:
			catdata = job_id.category_ids
		else:
			catdata = False

		if template:
			for line in template.wage_ids:
				if job_id and line.job_id.id == job_id.id:
					wage = line.starting_wage
				elif catdata:
					cat_id = False
					category_ids = [c.id for c in line.category_ids]
					for ci in catdata['category_ids']:
						if ci in category_ids:
							cat_id = ci
							break
					if cat_id:
						wage = line.starting_wage
				if line.is_default and default == 0:
					default = line.starting_wage
				if wage != 0:
					break
		if wage == 0:
			wage = default
		return wage
	
	#@api.model
	#def _needaction_domain_get(self):
	#	users_obj = self.env['res.users']
	#	domain = []
	#	if users_obj.has_group('hr.group_hr_manager'):
	#		domain = [('state', 'in', ['draft', 'contract_ending', 'trial_ending','pending_close'])]
	#		return domain
	#	return False

	@api.model
	def try_signal_ending_contract(self):
		d = datetime.now().date() + relativedelta.relativedelta(days=+30)
		contract_ids = self.search([('state', '=', 'open'),('date_end', '<=', d.strftime(OE_DFORMAT))])
		if contract_ids:
			contract_ids.write({'state':'contract_ending'})

	@api.model
	def try_signal_contract_completed(self):
		d = datetime.now().date()
		contact_ids = self.search([('state', '=', 'open'),('date_end', '<', d.strftime(OE_DFORMAT))])
		for contract in contact_ids:
			vals = {
				'name': contract.date_end or time.strftime(OE_DFORMAT),
				'employee_id': contract.employee_id.id,
				'reason': 'contract_end',
			}
			self.setup_pending_close(contract,vals)

	@api.multi
	def setup_pending_close(self, term_vals):
		"""Start employee deactivation process."""
		self.ensure_one()
		dToday = datetime.now().date()

		# If employee is already inactive simply end the contract
		if not self.employee_id.active:
		    self.contract_close()
		    return

		# Ensure there are not other open contracts
		open_contract = False
		for emp_contract in self.employee_id.contract_ids:
			if emp_contract.id == self.id or emp_contract.state == 'draft':
				continue
			if ((not emp_contract.date_end or datetime.strptime(emp_contract.date_end,OE_DFORMAT).date() >= dToday) and emp_contract.state != 'close'):
				open_contract = True

		# Don't create an employment termination if the employee has an open contract or if this contract is already in the 'close' state.
		if open_contract or self.state == 'close':
			return

		# Also skip creating an employment termination if there is already one in progress for this employee.
		term_ids = self.env['hr.employee.termination'].search([('employee_id', '=', self.employee_id.id),('state', 'in', ['draft', 'confirm'])])
		if len(term_ids) > 0:
			return
			
		self.env['hr.employee.termination'].create(term_vals)

		# Set the contract state to pending completion
		self.contract_pending_close()

		# Set employee state to pending deactivation
		self.employee_id.state_pending_inactive()
		
		if datetime.strptime(term_vals.get('terminate_date'),OE_DFORMAT).date() <= dToday:
			self.contract_close()	

	def try_signal_ending_trial(self):
		d = datetime.now().date() + relativedelta.relativedelta(days=+10)
		contract_ids = self.search([('state', '=', 'trial'),('trial_date_end', '<=', d.strftime(OE_DFORMAT))])
		if contract_ids:
			contract_ids.write({'state':'trial_ending'})
		
	def try_signal_open(self):
		d = datetime.now().date() + relativedelta.relativedelta(days=-5)
		contract_ids = self.search([('state', '=', 'trial_ending'),('trial_date_end', '<=', d.strftime(OE_DFORMAT))])
		if contract_ids:
			contract_ids.confirm_contract()

	
	@api.multi
	def state_trial(self):		
		for contract in self:		
			contract.state = 'trial'
			# if the Employee is new Hiring, Change his Status to On-Board
			if contract.employee_id.status == 'new':
				contract.employee_id.suspend_security().state_inactive()
		return True


	@api.multi
	def confirm_contract(self):		
		for contract in self:
			contract.sudo().state = 'open'
			# if the Employee is new Hiring, Change his Status to Active
			if contract.employee_id.status == 'new':
				#contract.employee_id.suspend_security().state_active()
				contract.employee_id.sudo().state_active()

	@api.multi
	def contract_pending_close(self):
		for contract in self:		
			contract.state = 'pending_close'			

	@api.multi
	def contract_close(self):
		for contract in self:		
			vals = {
				'state': 'close',
				'date_end': contract.date_end or time.strftime(OE_DFORMAT),
				'job_id': False,
				'end_job_id': contract.job_id.id,
			}
			contract.write(vals)
			#contract.employee_id.suspend_security().state_inactive()

	#def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
	#	res = models.Model.fields_view_get(self, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
	#	can_create = self._context.get('can_create', True)
	#	update = not can_create and view_type in ['form', 'tree']
	#	if update:
	#		doc = etree.XML(res['arch'])
	#		if not can_create:
	#			for t in doc.xpath("//"+view_type):
	#			    t.attrib['create'] = 'false'
	#		res['arch'] = etree.tostring(doc)
	#	return res
	
	
	def end_contract(self):
		context = self._context.copy()
		context.update({'end_contract_id': self.id})
		return {
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.contract.end',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
		}
	



