import time
from datetime import datetime
from dateutil import relativedelta
import pdb
from odoo import api, fields, models


class StaffArrearWizard(models.TransientModel):
	_name = "staff.arrear.wizard"
	_description = "Staff Arrears"
	
	employee_id = fields.Many2one('hr.employee', 'Employee')
	center_id = fields.Many2one('sos.center',related='employee_id.center_id', string='Center',readonly=False, store=True)
	date = fields.Date('Effecting Date')
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),],'Status', default='draft')
	line_ids = fields.One2many('staff.arrear.lines.wizard','arrear_id','Arrear Lines')

	@api.multi
	def generate_entries(self):
		salary_input_obj = self.env['hr.salary.inputs']
		if self.employee_id:
			for line in self.line_ids:
				res = {
					'employee_id': self.employee_id.id,
					'center_id': self.center_id.id,
					'date': self.date,
					'state': self.state or 'draft',
					'amount' : line.amount or 0.0,
					'name' : line.name,
					'description' : line.description,
				}								
				salary_input_rec = salary_input_obj.suspend_security().create(res)	
		return {'type': 'ir.actions.act_window_close'}


class StaffArrearLinesWizard(models.TransientModel):
	_name ='staff.arrear.lines.wizard'
	_description = 'Staff Arrear Lines'
	
	name = fields.Selection([('SBNS','Bonus of Employee'),('ADV','Advance against Salary'),('ARS','Arrear'),('FINE','Late/Absent Fine'),('LOAN','Personal Loan'), \
			('MOBD','Mobile Deduction'),('TAXD','Tax Deduction'),('RENTD','Rent Deduction'),('FOODD','Food Deduction'),('INSD','Insurance Deduction'),('FAP','Fine and Penalty'),('OD','Other Deduction')],'Category', required=True)
	amount = fields.Float(string='Amount', required=True)
	description = fields.Text('Description')
	arrear_id = fields.Many2one('staff.arrear.wizard', 'Arrear')					

	




          
