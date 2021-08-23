from datetime import datetime
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class projects_salary_advice_rep(models.TransientModel):
	_name = 'projects.salary.advice.rep'
	_description = 'Projects Salary Advice'
	
	
	@api.model
	def _get_advice_id(self):
		adv_id = self.env['guards.payroll.advice'].browse(self._context.get('active_id',False))
		if adv_id:
			return adv_id.id
		return True	
		
	#Fields	
	advice_id = fields.Many2one('guards.payroll.advice', "Advice", required=True,default=_get_advice_id)
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos_payroll.report_projects_salary_adice').with_context(landscape=True).report_action(self, data=datas)
