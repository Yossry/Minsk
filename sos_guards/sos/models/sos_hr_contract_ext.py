import pdb
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp

class SOSSimAllotment(models.Model):
	_name = "sos.sim.allotment"
	_description = "Sim Allotment"
	_inherit = ['mail.thread']
	
	name = fields.Char('SIM No.', track_visibility='always')
	assignee = fields.Char('Full Name', track_visibility='always')
	employee_id = fields.Many2one('hr.employee','Employee', track_visibility='always')
	center_id = fields.Many2one('sos.center', 'Region', track_visibility='always')
	limit = fields.Float('Limit', track_visibility='always')
	allotment_date = fields.Date('Allotment Date', track_visibility='always')
	status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive'), ('blocked','Blocked'), ('suspended','Suspended')], 'Status', default='active', track_visibility='always')
	bill_ids = fields.One2many('sos.sim.bills','sim_id','Bills')
	
	_sql_constraints = [
		('employee_sim_uniq', 'unique(name, employee_id)', 'The number should be unique for an employee!'),
	]

	@api.multi
	def unlink(self):
		if self.status == 'active':
			raise UserError(('You can not delete the Record which are not in active.'))
		ret = super(SOSSimAllotment, self).unlink()
		return ret


class SOSSimBills(models.Model):
	_name = "sos.sim.bills"
	_description = "Sim Bills"
	_inherit = ['mail.thread']

	@api.multi
	@api.depends('sim_id','limit','inv_amount')		
	def compute_deduction(self):
		for rec in self:
			deduction = 0.0
			if rec.inv_amount > rec.limit:
				deduction = rec.inv_amount - rec.limit
				rec.deduction = abs(deduction) or 0
	
	name = fields.Char('Name', track_visibility='always')	
	sim_number = fields.Char('SIM No.', track_visibility='always')
	bill_month = fields.Char('Bill Month', track_visibility='always')
	inv_amount = fields.Float('Amount', track_visibility='always')
	bill_date = fields.Date('Bill Date', track_visibility='always')
	sim_id = fields.Many2one('sos.sim.allotment','Sim No')
	limit = fields.Float(related='sim_id.limit', string='Limit', store=True)
	deduction = fields.Float('Deduction', compute='compute_deduction')
	state = fields.Selection([('draft', 'Draft'), ('validate', 'Validated'), ('done','Done')], 'Status', default='draft', track_visibility='always')

	@api.model	
	def create(self,vals):
		sim_number = vals.get('sim_number',False)
		if sim_number:
			sim_id = self.env['sos.sim.allotment'].search([('name','=', sim_number), ('status','=','active')])
			if sim_id:
				vals.update({
					'sim_id': sim_id.id,
					'limit' : sim_id.limit or 0.0
				})	
		return super(SOSSimBills, self).create(vals)
		
	@api.multi
	def write(self, vals):
		sim_number = vals.get('sim_number',False)		
		if sim_number:
			sim_id = self.env['sos.sim.allotment'].search([('name','=', sim_number), ('status','=','active')])
			if sim_id:
				vals.update({
					'sim_id': sim_id.id,
					'limit' : sim_id.limit or 0.0
				})
				
		return super(SOSSimBills, self).write(vals)
		
	@api.multi	
	def validate_bills(self):
		salary_input_obj = self.env['hr.salary.inputs']
		for rec in self:
			employee_id = False
			if rec.deduction > 0:
				employee_id = rec.sim_id.employee_id
				if not employee_id:
					employee_id = self.env['hr.employee'].search([('mobile_phone','=',rec.sim_number)])
				if not employee_id:
					employee_id = self.env['hr.employee'].search([('work_phone','=',rec.sim_number)])
				if not employee_id:
					#sim_number = rec.sim_number[-11:]
					employee_id = self.env['hr.employee'].search([('mobile_phone','=',rec.sim_number[-11:])])
				
				if employee_id:		
					res = {
						'employee_id': employee_id.id,
						'center_id': employee_id.center_id.id,
						'date': rec.bill_date,
						'state': rec.state or 'draft',
						'amount' : rec.deduction or 0.0,
						'name' : 'MOBD',
						#'description' : rec.description,
					}								
					salary_input_rec = salary_input_obj.suspend_security().create(res)
					rec.state = 'validate'
				else:
					raise UserError(_('Does not Find the Employee Related to the A Number No. in the List'))	
		
	@api.multi	
	def done_bills(self):
		self.write({'state':'done'})
		

## HR Segmentation
class HRSegmentation(models.Model):
	_name = "hr.segmentation"
	_description = "HR Segmentation"

	name = fields.Char('Name')
	code = fields.Char('Code')
	sub_segment_ids = fields.One2many('hr.sub.segmentation', 'segment_id',string='Sub Segments')

## HR Sub Segmentation	
class HRSubSegmentation(models.Model):
	_name = "hr.sub.segmentation"
	_description = "HR Sub Segmentation"

	name = fields.Char('Name')
	code = fields.Char('Code')
	segment_id = fields.Many2one('hr.segmentation','Segment')	
	

## Staff Transfer History	
class HRStaffTransferHistory(models.Model):
	_name = "hr.staff.transfer.history"
	_description = "HR Staff Transfer History"

	name = fields.Char('Name')
	employee_id = fields.Many2one('hr.employee', 'Employee')
	segment_id = fields.Many2one('hr.segmentation', string='Segment')
	sub_segment_id = fields.Many2one('hr.sub.segmentation',string='Sub Segment')
	department_id = fields.Many2one('hr.department', string='Department')		
	job_id = fields.Many2one('hr.job',string='Job')
	parent_id = fields.Many2one('hr.employee',string='Manager')
	coach_id = fields.Many2one('hr.employee',string='Coach')
	center_id = fields.Many2one('sos.center',string='Center')
	transfer_date = fields.Date('Transfer Date',default=lambda *a: str(datetime.now())[:10])




