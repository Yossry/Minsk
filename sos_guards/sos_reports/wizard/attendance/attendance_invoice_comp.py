import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models

class AttendanceInvoiceComp(models.TransientModel):
	_name = 'attendance.invoice.comp'	
	_description = 'Attendance Invoice Comparison'
		
	project_ids = fields.Many2many('sos.project', string='Filter on Projects', help="""Only selected Projects will be printed. Leave empty to print all Projects.""")                            
	center_ids = fields.Many2many('sos.center', string='Filter on Centers', help="""Only selected Centers will be printed. Leave empty to print all Centers.""")                          
	filters = fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True,default="filter_date")
	date_from = fields.Date("Start Date", default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10])
	date_to = fields.Date("End Date",default=lambda self:str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10])
 
	@api.onchange('filters')
	def onchange_filter(self):
		res = {'value': {}}
		if filter == 'filter_no':
			res['value'] = {'date_from': False ,'date_to': False}
		if filter == 'filter_date':
			res['value'] = {
					'date_from': str(datetime.now() + relativedelta.relativedelta(months=-1, day=1))[:10], 
					'date_to': str(datetime.now() + relativedelta.relativedelta(months=-1, day=31))[:10]
					}
		return res
	
	@api.multi
	def print_report(self):
		self.ensure_one()
		[data]=self.read()
		datas={
			'ids': [],
			'model': 'sos.guard.attendance',
			'form' : data
			}
		return self.env.ref('sos_reports.report_attendance_invoice_comp').with_context(landscape=True).report_action(self, data=datas,config=False)
		
		
