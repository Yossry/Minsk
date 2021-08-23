import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class LegderSummaryReport(models.TransientModel):
	_name = "ledger.summary.report"
	_description = "Ledger Summary Report Wizard"
		
	date_start = fields.Date('Starting Month', required=True,default=lambda *a: str(datetime.now() + relativedelta.relativedelta(day=1))[:10])
	account_id = fields.Many2one('account.account','Account',required=True)
	dimension_id = fields.Many2one('analytic.dimension','Dimension',required=True)
	display_att = fields.Selection([('debit','Debit'),('credit','Credit'),('balance','Balance'),('cbalance','(Balance)')],string="Display Attribute",default='debit',required=True)
	interval = fields.Selection([('month','Month')],string='Interval',default='month',required=True)
	interval_count = fields.Integer('Interval Count',default=12)

	@api.multi
	def print_report(self):		
		self.ensure_one()
		[data] = self.read()
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'res.partner',
			'form': data
		}		
		if data['interval'] == 'month' and (data['interval_count'] < 2 or data['interval_count'] > 12):
			raise UserError(_('For Month Interval, the Interval Count should be between 2 and 12'))
		return self.env.ref('aarsol_accounts.ledgersummary').report_action(self, data=datas, config=False)