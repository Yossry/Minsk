import pdb
import time
from openerp import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class SOSGuardsAccountBlock(models.Model):
	_name = "sos.guards.account.block"
	_inherit = ['mail.thread']
	_description = "Guards Account Block"
	_order = 'id desc'

	@api.multi
	@api.depends('employee_id')
	def get_bankacc(self):
		for rec in self:
			if rec.employee_id and not rec.bankacc:
				rec.bankacc = rec.employee_id.bankacc
	
	@api.onchange('project_id')					
	def onchange_project(self):
		self.center_id = False
		self.post_id = False
	
	@api.onchange('center_id')					
	def onchange_center(self):
		self.post_id = False
	
	@api.onchange('post_id')					
	def onchange_post(self):
		self.employee_id = False
		self.code = ''			
		
	name = fields.Char('Name')
	center_id = fields.Many2one('sos.center', string='Center',required=False, index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	project_id = fields.Many2one('sos.project', required=False, string = 'Project', index=True, readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange')
	post_id = fields.Many2one('sos.post', string = 'Post', index=True, required=False, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee','Employee', required=False)
	code = fields.Char(related='employee_id.code' ,string='Code', store=True)
	date = fields.Date('Date',default=lambda self: datetime.today().strftime('%Y-%m-%d'),track_visibility='onchange')
	bank_id = fields.Many2one('sos.bank',string='Bank Name', required="1")
	bankacctitle = fields.Char(string='Account Title', required="1")
	accowner = fields.Selection( [ ('selff','Self'),('acc','Accountant'), ('rm','Regional Manager'), ('sp','Supervisor'),('other','Other')],'Account Owner')
	bankacc = fields.Char(string='Account No', required="1")
	guard_count = fields.Integer(string='Total Account#', compute='get_guard_count', store=True)
	state = fields.Selection([('draft','Draft'),('block','Block')],'Status',default='draft', track_visibility='onchange')
	remarks = fields.Text('Remarks', compute='get_guard_count', store=True)

	@api.model
	def create(self, vals):
		if vals.get('employee_id',False):
			emp_rec = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
			if emp_rec:
				emp_name = emp_rec.name or ''
				ref = emp_rec.code or ''
				vals['name'] = ref + '/' + emp_name
				#if not vals['bankacc']:
				#	vals['bankacc'] = emp_rec.bankacc or ''
				
		if not vals.get('employee_id',False):
			vals['name'] =  vals.get('bankacctitle') + '/' + vals.get('bankacc')
		result = super(SOSGuardsAccountBlock, self).create(vals)
		return result
		
	@api.multi
	def unlink(self):
		if self.state != 'draft':
			raise UserError(('You can not delete a Record which are not in Draft State'))
		ret = super(SOSGuardsAccountBlock, self).unlink()
		return ret

	@api.multi
	@api.depends('employee_id','bankacc','bank_id')
	def get_guard_count(self):
		for rec in self:
			text = ''
			cnt = 0
			account = rec.bankacc or ''
			count = self.env['hr.employee'].search_count([('bankacc','=',account)])
			emps = self.env['hr.employee'].search([('bankacc','=',account)])
			if emps:
				for emp in emps:
					cnt +=1
					text += str(cnt) + '):- ' +  emp.code + '-' + emp.name + " / " + emp.fathername + " Account# " + emp.bankacc +"\n"
				rec.remarks = text	 
			rec.guard_count = count or 0				

	@api.multi		
	def block_account(self):
		for rec in self:
			account = self.bankacc
			employee_recs = self.env['hr.employee'].search([('bankacc','=',account)])
			if employee_recs:
				for employee_rec in employee_recs:
					#MGS in HR EMPLOYEE
					msg1 = "Account number " + employee_rec.bankacc + " has been blocked."
					employee_rec.message_post(msg1)
					
					#MGS
					msg2 = "Account number " + employee_rec.bankacc + " has been blocked of Guard " + employee_rec.name
					rec.message_post(msg2)
					employee_rec.bankacc = ''
				rec.state='block'
			else:
				raise UserError(_('No Employee Found with this Account Number in the Employee Profiles, please Check the Account number.'))