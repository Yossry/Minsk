
import time
import pdb
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountReportGeneralLedger(models.TransientModel):
	_inherit = "account.report.general.ledger"
	
	
	journal_ids = fields.Many2many('account.journal', string='Journals', required=False, default=lambda self: self.env['account.journal'].search([('id','=',0)]))
	account_ids = fields.Many2many('account.account', string='Accounts')
	
		
	@api.multi
	def pre_print_report(self, data):		
		data = super(AccountReportGeneralLedger,self).pre_print_report(data)
		data['form'].update(self.read(['account_ids'])[0])
		return data
        
	
	
	
	
