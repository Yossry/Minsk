import json
import pdb
import time
import math
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil import relativedelta

class SOSGuardsExitForm(models.Model):
	_name = "sos.guards.exit.form"
	_inherit = ['mail.thread']
	_description = "Guards Exit Form"
	_order = "id"
	
	#@api.onchange('project_id')					
	#def onchange_project(self):
	#	self.center_id = False
	#	self.post_id = False
	
	#@api.onchange('center_id')					
	#def onchange_center(self):
	#	self.post_id = False
	
	#@api.onchange('post_id')					
	#def onchange_post(self):
	#	self.employee_id = False
	#	self.code = ''
	
	@api.onchange('code')					
	def onchange_employee(self):
		employee_id = False
		employee_id = self.env['hr.employee'].search([('code','=',self.code)])
		if employee_id:
			self.employee_id = employee_id and employee_id.id or False
			self.cnic = employee_id.cnic and employee_id.cnic or ''
			self.appointment_date = employee_id.appointmentdate and employee_id.appointmentdate or ''
			self.project_id = employee_id.project_id and employee_id.project_id.id or False
			self.center_id = employee_id.center_id and employee_id.center_id.id or False
			self.post_id = employee_id.current_post_id and employee_id.current_post_id.id or False ## here is the Read Access Issue os i use the sudo(), later on i will check it
			self.bank_id = employee_id.bank_id and employee_id.bank_id.id or False
			self.accowner = employee_id.accowner and employee_id.accowner or False
			self.bankacctitle = employee_id.bankacctitle and employee_id.bankacctitle or ''
			self.bankacc = employee_id.bankacc and employee_id.bankacc or ''
			self.date = fields.Date.today()

	@api.multi
	@api.depends('employee_id','post_id')
	def get_joining_post(self):
		for rec in self:
			joining_post = self.env['sos.guard.post'].search([('employee_id','=',rec.employee_id.id)], order='fromdate', limit=1)
			rec.joining_post = joining_post.post_id.id or False
		
	@api.multi
	@api.depends('salary','salary_amt','security','security_amt')
	def get_security_info_json(self):
		for rec in self:
			rec.security_widget = json.dumps(False)
			info = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
			lines = self.env['guards.payslip.line'].search([('employee_id','=',rec.employee_id.id),('code','=', 'GSD')], order='date_from')
			if lines:
				for line in lines:
					info['content'].append({
						'name': line.slip_id.name,
						'date': str(line.slip_id.date_from),
						'ref': line.name or '',
						'amount': line.total and abs(line.total) or 0,
					})
				rec.security_widget = json.dumps(info)

	name = fields.Char('Name')
	center_id = fields.Many2one('sos.center', string='Center',required=True, index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=True, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=True, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee','Employee', required=True)
	code = fields.Char(string='Code',required=True)
	cnic = fields.Char('CNIC')
	date = fields.Date('Termination Date',track_visibility='onchange')
	appointment_date = fields.Date('Appointment Date',track_visibility='onchange')
	joining_post = fields.Many2one('sos.post', string = 'Joining Post', compute='get_joining_post', store=True)
	
	bank_id = fields.Many2one('sos.bank',string='Bank Name', required=False)
	bankacctitle = fields.Char(string='Account Title', required=False)
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner')
	bankacc = fields.Char(string='Account No', required=False)
	salary = fields.Boolean('Salary')
	salary_amt = fields.Float('Salary Amount') #salary_amt = fields.Float('Salary Amount',compute="get_salary_amt", store=True)
	security = fields.Boolean('Security')
	security_amt = fields.Float('Security Amount', compute="get_security_amt", store=True)
	total_dues = fields.Float('Total Dues', compute="compute_dues", store=True)
	
	company_card = fields.Integer('Company Card')
	uniform = fields.Integer('Uniform')
	shoes = fields.Integer('Shoes')
	cap = fields.Integer('Cap')
	belt = fields.Integer('Belt')
	
	t_shirt = fields.Integer('T-Shirt')
	trouser = fields.Integer('Trouser')
	shalwa_kameez = fields.Integer('Shalwar kameez')
	jersey_jacket = fields.Integer('Jersey/Jacket ')
	
	other_accessories = fields.Char('Other Accessories')
	
	slip_comments = fields.Char('Slip Comments')
	state = fields.Selection([('draft','Draft'),('store','Store'),('accounts', 'Accounts'),('disburse','Disburse'),('close','Close') ],'Status',default='draft', track_visibility='onchange')
	remarks = fields.Text('Remarks',compute='compute_remarks', store=True)
	#uniform_return_id = fields.Many2one('sos.uniform.return', string='Uniform Return Ref.')
	security_widget = fields.Text(compute='get_security_info_json')
	
	@api.multi
	def _check_guard_code(self):
		for record in self:
			if record.code:
				fnd = False
				fnd = self.env['sos.guards.exit.form'].search([('code','=',record.code)])
				if fnd:
					return False			
		return True

	
	@api.model	
	def create(self,vals):
		obj_seq = self.env['ir.sequence']
		st_number = obj_seq.next_by_code('sos.guards.exit.form')
		vals.update({
			'name': st_number,
		})
		new_rec = super(SOSGuardsExitForm, self).create(vals)
		if vals['employee_id']:
			emp = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
			if not emp.exit_form:
				emp.exit_form = True
			if new_rec:
				emp.exit_form_id = new_rec.id
		return new_rec
	
	@api.multi
	def unlink(self):
		if self.state == 'close':
			raise UserError(('You can not delete a Record which are in Close State'))

		return_id = self.env['sos.uniform.return'].search([('guard_id','=',self.employee_id.id),('state','=','draft'),('date','=',self.date)])	
		if return_id:
			msg1 = "Uniform Return Entry is deleted against the Exit Form " + self.name + ". Return reference: " +  return_id.name 
			self.employee_id.message_post(body=msg1)
			return_id.unlink()
		
		if self.employee_id.exit_form:
			self.employee_id.exit_form = False
			self.employee_id.exit_form_id = False
			self.employee_id.security_refund = True
		
		msg2 = "Exit Form " + self.name + " is deleted." 
		self.employee_id.message_post(body=msg2)
		ret = super(SOSGuardsExitForm, self).unlink()
		return ret	
	
	@api.multi	
	@api.depends('employee_id','post_id')				
	def get_joining_post(self):
		for rec in self:
			joining_post = self.env['sos.guard.post'].search([('employee_id','=',rec.employee_id.id)], order='fromdate', limit=1)
			rec.joining_post = joining_post.post_id.id or False
			
	@api.multi
	@api.depends('employee_id','post_id','security')				
	def get_security_amt(self):
		for rec in self:
			amt = 0
			lines = self.env['guards.payslip.line'].search([('employee_id','=',rec.employee_id.id),('code','=', 'GSD')])
			if lines:
				amt = sum(line.total for line in lines)
				rec.security_amt = abs(amt) or 0
		return abs(amt) or 0
	
	@api.multi
	@api.depends('employee_id','post_id','security')				
	def get_salary_amt(self):
		for rec in self:
			dt = datetime.strptime(rec.date,"%Y-%m-%d")
			first_day = (dt + relativedelta.relativedelta(day=1))
			last_day = (dt + relativedelta.relativedelta(day=31))
			amt = 0
			payslip = self.env['guards.payslip'].search([('employee_id','=',rec.employee_id.id),('date_from','>=', first_day),('date_to','=',last_day)])
			if payslip:
				line = self.env['guards.payslip.line'].search([('slip_id','=',payslip.id),('code','=','NET')])
				rec.salary_amt = line.total or 0
				
	@api.multi
	@api.depends('salary_amt','security_amt')				
	def compute_dues(self):
		for rec in self:
			rec.total_dues = rec.salary_amt + rec.security_amt	or 0.0
	
	@api.multi
	@api.depends('employee_id','cnic')				
	def compute_remarks(self):
		for rec in self:
			emp_name = rec.employee_id.name or ''
			father_name = rec.employee_id.fathername or ''
			cnic = rec.employee_id.cnic or ''
			txt = "I " + emp_name + " S/O " + father_name + ", my CNIC " + cnic + " state that i am leaving this company and i have return all the accessories that company has provided me. Company has cleared my all the due. Nothing is pending to the company." 		
			rec.remarks = txt		
	
	@api.multi
	def exit_form_store(self):
		for rec in self:
			vals = {
				'center_id' : rec.center_id and rec.center_id.id or False,
				'project_id' : rec.project_id and rec.project_id.id or False,
				'post_id' : rec.post_id and rec.post_id.id or False,
				'guard_id' : rec.employee_id.guard_id and rec.employee_id.guard_id.id or False,
				'guard_employee_id' : rec.employee_id and rec.employee_id.id or False,
				'date' : rec.date and rec.date,
				'receive_date' : rec.date and rec.date,
				'state' : 'draft',
				}
			ret_id = self.env['sos.uniform.return'].sudo().create(vals)
			
			if rec.uniform > 0:
				self.env.cr.execute('insert into sos_product_uniform_return (return_id,product_id) values(%s,%s)',(ret_id.id,2))
			
			if rec.shoes > 0:
				self.env.cr.execute('insert into sos_product_uniform_return (return_id,product_id) values(%s,%s)',(ret_id.id,3))
				
			if rec.cap > 0:
				self.env.cr.execute('insert into sos_product_uniform_return (return_id,product_id) values(%s,%s)',(ret_id.id,4))
			
			if rec.belt > 0:
				self.env.cr.execute('insert into sos_product_uniform_return (return_id,product_id) values(%s,%s)',(ret_id.id,5))
				
			if rec.company_card > 0:
				self.env.cr.execute('insert into sos_product_uniform_return (return_id,product_id) values(%s,%s)',(ret_id.id,84))					
			
			#rec.uniform_return_id = ret_id and ret_id.id or False
			rec.state='store'
				
	@api.multi
	def exit_form_monitor(self):
		for rec in self:
			rec.state='monitor'
	
	@api.multi
	def exit_form_accounts(self):
		for rec in self:
			rec.state='accounts'
			
	@api.multi
	def exit_form_disburse(self):
		for rec in self:
			rec.state='disburse'
	@api.multi
	def exit_form_close(self):
		for rec in self:
			rec.employee_id.security_refund = True
			rec.state='close'