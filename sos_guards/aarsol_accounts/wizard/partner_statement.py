import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import tools
from odoo import models, fields, api, _

class partner_statement_wizard(models.TransientModel):
	_name = 'partner.statement.wizard'

	date_from = fields.Date('Start Date', required=True,default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-2,day=1))[:10])
	date_to = fields.Date('End Date', required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
	partner_id = fields.Many2one('res.partner', 'Partner',required=True,default=lambda self: self._context.get('active_id',False) )


	def _build_contexts(self, data):
		result = {}
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['partner_id'] = data['form']['partner_id'] or False
		return result

	
	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': [],
			'model': 'res.partner',
			'form': data
		}
		
		return self.env.ref('aarsol_accounts.partnerstatement').report_action(self, data=datas, config=False)
		
	
