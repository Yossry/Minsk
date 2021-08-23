import time
from datetime import datetime
from dateutil import relativedelta
import pdb
from odoo import api, fields, models

class staff_payslips_cron_wizard(models.TransientModel):
	_name ='staff.payslips.cron.wizard'
	_description = 'Generate Cron Entries'
	
	@api.onchange('date_from','date_to')
	@api.one
	def _compute_employee(self):
		employee_ids = False
		emps = self.env['hr.employee'].search([('status','in',['new','active','onboarding']),('department_id','!=',29),('is_guard','=',False)],order='department_id, code')
		if emps:
			employee_ids = emps.ids
		self.employee_ids = employee_ids
	
	date_from = fields.Date("Date From",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("Date To",default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	employee_ids = fields.Many2many('hr.employee', string='Filter on Employees', help="Only selected Employees Salaries will be generated.")
	
	@api.multi
	def generate_cron_entry(self):
		cron_slip_pool = self.env['staff.payslip.cron']
		emp_pool = self.env['hr.employee']
		att_pool = self.env['hr.employee.month.attendance']

		for data in self:		
			for emp in data.employee_ids:
				att_domain = [('date','>=',data.date_from),('date','<=',data.date_to),('slip_id','=',False),('employee_id','=',emp.id)]
				att_ids = att_pool.search(att_domain)
				if att_ids:
					att_ids.write({'state':'counted'})

					res = {
						'employee_id': emp.id,
						'date_from': data.date_from,
						'date_to': data.date_to,
						'state': 'draft',
						'center_id': emp.center_id.id,
					}								
					cron_rec = cron_slip_pool.sudo().create(res)
					
			
		return {'type': 'ir.actions.act_window_close'}





          
