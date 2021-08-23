import pdb
from odoo import api, fields, models, _

class sos_guards_data_report(models.TransientModel):

	_name = 'sos.guards.data.report'
	_description = 'Guard Data Report'

	project_id = fields.Many2one('sos.project', string='Projects')
	center_id = fields.Many2one('sos.center', string='Centers')
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'hr.employee',
			'form' : data
		}
		return self.env.ref('sos.report_guards_data').with_context(landscape=True).report_action(self, data=datas)
