import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models

class guards_payslip_runs(models.TransientModel):
	_name ='guards.payslip.runs'
	_description = 'Generate payslips for all Selected Runs'
	
	payslip_run_ids = fields.One2many('guards.payslip.run', 'advice_id', 'Payslip Batches')		
    
	def compute_sheet(self, cr, uid, ids, context=None):
		emp_pool = self.pool.get('hr.employee')
		slip_pool = self.pool.get('guards.payslip')
		run_pool = self.pool.get('guards.payslip.run')
		slip_ids = []
		if context is None:
			context = {}
		data = self.read(cr, uid, ids, context=context)[0]
		run_data = {}
		if context and context.get('active_id', False):
			run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note'])
		from_date =  run_data.get('date_start', False)
		to_date = run_data.get('date_end', False)
		credit_note = run_data.get('credit_note', False)
		if not data['employee_ids']:
			raise osv.except_osv(_("Warning !"), _("You must select employee(s) to generate payslip(s)."))
		for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
			slip_data = slip_pool.on_change_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
			res = {
				'employee_id': emp.id,
				'name': slip_data['value'].get('name', False),
				'struct_id': slip_data['value'].get('struct_id', False),
				'contract_id': slip_data['value'].get('contract_id', False),
				'payslip_run_id': context.get('active_id', False),
				'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
				'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
				'date_from': from_date,
				'date_to': to_date,
				'credit_note': credit_note,
			}
			slip_ids.append(slip_pool.create(cr, uid, res, context=context))
		slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
		return {'type': 'ir.actions.act_window_close'}




