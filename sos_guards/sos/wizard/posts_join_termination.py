import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _

class posts_join_termination(models.TransientModel):

	_name = 'posts.join.termination'
	_description = 'Posts Join Termination Report'
	
	date_from = fields.Date('Date From', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date('Date To', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
	order_by = fields.Selection([('post','Post'),('center','Center'),('project','Project'),('startdate','Start Date'),('enddate','End Date')],'Order By',default='center')
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")     
	report_name = fields.Selection( [('salary_advised_aeroo','Base Post'),('salary_advised_post_aeroo','Post Wise')],'Report',default='salary_advised_post_aeroo')
	
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.post',
			'form' : data,
		}
		return self.env.ref('sos.report_posts_join_termination').with_context(landscape=True).report_action(self, data=datas, config=False)


