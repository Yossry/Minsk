import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class salary_invoice_comp(models.TransientModel):
	_name = 'salary.invoice.comp'	
	_description = 'Salary Invoice Comparison'
	
		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                            
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          
	target_move = fields.Selection([('all', 'All Entries'),('diff', 'Entries having Difference'),('more', 'Entries having Excess Salary'),('less', 'Entries having Less Salary')], 'Target Moves')		
	filters = fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True)
	date_from = fields.Date("Start Date")
	date_to = fields.Date("End Date")
	centralize = fields.Boolean('Activate Centralization', help='Uncheck to display all the details of centralized accounts.')

	_defaults = {		
		'filters': 'filter_date',
		'date_from': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10],
		'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10],
		'centralize': True,		
		'target_move': 'all',
	}   
	
	@api.onchange('filters')
	def onchange_filter(self):
		res = {'value': {}}
		if filter == 'filter_no':
			res['value'] = {'date_from': False ,'date_to': False}
		if filter == 'filter_date':
			res['value'] = {'date_from': str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10], 'date_to': str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10]}
		return res
		
	
	
	@api.multi
	def print_report(self):
				
		data = {'ids': self._context.get('active_ids', [])}
		data.update({'form': self.read([])[0]})

		return self.env['report'].with_context(landscape=True).get_action(self, 'sos_payroll.report_salary_invoicecomp', data=data)
		
		
