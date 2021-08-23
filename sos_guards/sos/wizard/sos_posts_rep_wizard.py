import pdb
import time
from odoo import api, fields, models, _


class sos_posts_report_wizard(models.TransientModel):
	
	_name = "sos.posts.report.wizard"
	_description = "SOS Posts Report"
	
	center_id = fields.Many2one('sos.center', 'Center', required=True)
	city_id = fields.Many2one('sos.city', 'City')

	
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.post',
			'form' : data
		}
		return self.env.ref('sos.report_posts_address').with_context(landscape=True).report_action(self, data=datas)
