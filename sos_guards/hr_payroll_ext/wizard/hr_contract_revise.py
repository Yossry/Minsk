import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
from openerp import models, fields, api, _

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()

class HRContractRevise(models.TransientModel):
	_name = 'hr.contract.revise'
	_description = 'HR Contract Revise Wizard'
	
	@api.model
	def _get_contract_id(self):
		contract_id = self.env['hr.contract'].browse(self._context.get('active_id',False))
		if contract_id:
			return contract_id.id
		return True
	
	@api.depends('new_salary','new_transportation_allowance','new_acomodation_allowance','new_mobile_allowance','new_food_allowance','new_supplementary_allowance')
	@api.multi
	def _get_gross_salary(self):
		for rec in self:
			gross_salary = 0
			gross_salary = (rec.new_salary + rec.new_transportation_allowance + rec.new_acomodation_allowance + rec.new_mobile_allowance + rec.new_food_allowance + rec.new_supplementary_allowance)
			rec.new_gross_salary = gross_salary
		
	contract_id = fields.Many2one('hr.contract', 'Contract', required=True,default=_get_contract_id)
	employee_id = fields.Many2one(related='contract_id.employee_id', string='Employee')
	
	old_department_id = fields.Many2one('hr.department',related='contract_id.department_id', string='Old Department')		
	old_contract_date = fields.Date('Old Promotion Date', related='contract_id.date_start')		
	old_designation = fields.Many2one('hr.job', related='contract_id.job_id' ,string='Old Designation')
	old_salary = fields.Float('Old Salary', related='contract_id.wage')
	old_transportation_allowance = fields.Float('Old Transportation Allowance', related='contract_id.transportation_allowance')
	old_acomodation_allowance = fields.Integer('Old Housing Allowance', related='contract_id.acomodation_allowance')
	old_mobile_allowance = fields.Integer('Old Mobile Allowance', related='contract_id.mobile_allowance')
	old_food_allowance = fields.Integer('Old Food Allowance', related='contract_id.food_allowance')
	old_supplementary_allowance = fields.Float('Old Other Allowance', related='contract_id.supplementary_allowance')
	old_gross_salary = fields.Float(related='contract_id.gross_salary', string="Old Gross Salary")
	
	new_department_id = fields.Many2one('hr.department',string='Department')		
	new_contract_date = fields.Date('Promotion Date',default=lambda *a: str(datetime.now())[:10])		
	new_designation = fields.Many2one('hr.job',string='New Designation')
	new_salary = fields.Float('New Salary')
	new_transportation_allowance = fields.Float('Transportation Allowance')
	new_acomodation_allowance = fields.Integer('Housing Allowance')
	new_mobile_allowance = fields.Integer('Mobile Allowance')
	new_food_allowance = fields.Integer('Food Allowance')
	new_supplementary_allowance = fields.Float('Other Allowance')
	new_gross_salary = fields.Float(compute='_get_gross_salary', string="Gross Salary", store=True)
	remarks = fields.Text('Remarks') 
	
	def revise_contract(self):
		name_len = len(self.contract_id.name)
		old_name = self.contract_id.name[:-1]
		revision = self.contract_id.name[name_len-1:name_len]
		revision = int(revision) + 1
		new_name = old_name + str(revision)
			
		vals = {
			'name' : new_name, 
			'employee_id' : self.employee_id.id,
			'department_id' : self.new_department_id and self.new_department_id.id  or self.old_department_id.id or '',
			'job_id' : self.new_designation and self.new_designation.id or self.old_designation.id or '',
			'type_id' : self.contract_id.type_id.id,
			'struct_id' : self.contract_id.struct_id.id,
			'wage' : self.new_salary or self.old_contract_id.wage,
			'date_start' : self.new_contract_date,
			'schedule_pay' : 'monthly',
			'journal_id' : self.contract_id.journal_id.id,
			'acomodation_allowance' : self.new_acomodation_allowance or 0,
			'transportation_allowance' : self.new_transportation_allowance or 0,
			'supplementary_allowance' : self.new_supplementary_allowance or 0,
			'mobile_allowance' : self.new_mobile_allowance or 0,
			'food_allowance' : self.new_food_allowance or 0,
			'notes' : self.remarks or '',
			'state' : 'open',
			'pps_id' : 1,
			}	
		new_contract = self.env['hr.contract'].sudo().create(vals)
		new_contract.confirm_contract()
		
		#End Previous
		#self.contract_id.pps_id = False
		self.contract_id.contract_close()
		self.contract_id.date_end = str(strToDate(self.new_contract_date) + (relativedelta.relativedelta(days=-1)))
		
		return {'type': 'ir.actions.act_window_close'}
	
