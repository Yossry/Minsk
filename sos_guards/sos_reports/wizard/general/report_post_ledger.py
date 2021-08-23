
from openerp import api, fields, models
from datetime import datetime
from dateutil import relativedelta
import pdb

class post_ledger(models.TransientModel):
	_name = 'account.post.ledger'
	_description = 'Account Post Ledger'

	@api.model	
	def _get_post_ids(self):
		if self._context.get('active_model', False) == 'sos.post' and self._context.get('active_ids', False):
			return self._context['active_ids']
		
	date_from = fields.Date(string='Start Date',default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-6, day=1))[:10])
	date_to = fields.Date(string='End Date', default=lambda *a: str(datetime.now())[:10])
	initial_balance = fields.Boolean('Include Initial Balances', default=False,help='If you selected to filter by date or period, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
	post_ids = fields.Many2many('sos.post', string='Posts', help="""Only selected Posts will be Processed.""",default=_get_post_ids)	
	
	@api.multi
	def print_report(self,data):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = 'sos.post'
		data['form'] = self.read([])[0]
				
		return self.env['report'].with_context(landscape=True).get_action(self, 'sos_reports.report_postledger', data=data,)


