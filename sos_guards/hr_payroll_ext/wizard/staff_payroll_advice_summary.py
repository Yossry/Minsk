import pdb
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class StaffPayrollAdviceSummaryWiz(models.TransientModel):
	_name = "staff.payroll.advice.summary.wiz"
	_description = "Staff Advice Summary"
	
	@api.model
	def _get_advice_id(self):
		adv_id = self.env['hr.payroll.advice'].browse(self._context.get('active_id',False))
		if adv_id:
			return adv_id.id
		return True	
	
	#Columns
	advice_id = fields.Many2one('hr.payroll.advice',default=_get_advice_id)
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.payroll.advice',
			'form' : data
		}
		return self.env.ref('hr_payroll_ext.action_staff_summary_adivce_summary').with_context(landscape=False).report_action(self, data=datas)
