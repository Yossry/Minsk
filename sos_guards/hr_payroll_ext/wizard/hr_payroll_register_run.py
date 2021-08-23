
from datetime import datetime
from pytz import timezone

from odoo import api, fields, models, _

class payroll_register_run(models.TransientModel):

	_name = 'hr.payroll.register.run'
	_description = 'Pay Slip Creation'

	department_ids = fields.Many2many('hr.department','hr_department_payslip_run_rel','register_id', 'register_run_id','Departments')

	def create_payslip_runs(self):
		dept_pool = self.env['hr.department']
		ee_pool = self.env['hr.employee']
		slip_pool = self.env['hr.payslip']
		run_pool = self.env['hr.payslip.run']
		reg_pool = self.env['hr.payroll.register']

		register_id = self._context.get('active_id', False)
		if not register_id:
			raise UserError(_("Programming Error !\nUnable to determine Payroll Register Id."))

		if not self.department_ids:
			raise UserError(_("Warning !\nNo departments selected for payslip generation."))

		pr = reg_pool.browse(register_id)

		# DateTime in db is store as naive UTC. Convert it to explicit UTC and then convert that into the our time zone.
		user_tx = self.env.user.tz
		local_tz = timezone(user_tz)
		utc_tz = timezone('UTC')
		utcDTStart = utc_tz.localize(datetime.strptime(pr.date_start, '%Y-%m-%d %H:%M:%S'))
		localDTStart = utcDTStart.astimezone(local_tz)
		date_start = localDTStart.strftime('%Y-%m-%d')
		utcDTEnd = utc_tz.localize(datetime.strptime(pr.date_end, '%Y-%m-%d %H:%M:%S'))
		localDTEnd = utcDTEnd.astimezone(local_tz)
		date_end = localDTEnd.strftime('%Y-%m-%d')

		for dept in self.department_ids:
			run_res = {
				'name': dept.complete_name,
				'date_start': pr.date_start,
				'date_end': pr.date_end,
				'register_id': register_id,
			}
			run_id = run_pool.create(run_res)

			slip_ids = []
			ee_ids = ee_pool.search([('department_id', '=', dept.id)],order="name")
			for ee in ee_ids:
				slip_data = slip_pool.onchange_employee_id([],date_start, date_end,ee.id, contract_id=False)
				res = {
					'employee_id': ee.id,
					'name': slip_data['value'].get('name', False),
					'struct_id': slip_data['value'].get('struct_id', False),
					'contract_id': slip_data['value'].get('contract_id', False),
					'payslip_run_id': run_id,
					'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
					'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
					'date_from': pr.date_start,
					'date_to': pr.date_end,
				}
				slip_ids.append(slip_pool.create(res))
			slip_pool.compute_sheet(slip_ids)

		return {'type': 'ir.actions.act_window_close'}
