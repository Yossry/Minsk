import pdb
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class GuardsPayrollAdviceSummaryWiz(models.TransientModel):
	_name = "guards.payroll.advice.summary.wiz"
	_description = "Guard Advice Summary"
	
	@api.model
	def _get_advice_id(self):
		adv_id = self.env['guards.payroll.advice'].browse(self._context.get('active_id',False))
		if adv_id:
			return adv_id.id
		return True	
	
	#Columns
	advice_id = fields.Many2one('guards.payroll.advice',default=_get_advice_id)
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'guards.payroll.advice',
			'form' : data
		}
		return self.env.ref('sos_payroll.action_guards_summary_adivce_summary').with_context(landscape=False).report_action(self, data=datas)
