import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class ClientsVisitReport(models.AbstractModel):
	_name = 'report.sos.report_clientsvisit'
	_description = 'Client Visit Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')	
	
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_end= data['form']['date_end'] and data['form']['date_end']
		type= data['form']['type'] and data['form']['type'] or False

		if type in ('supervisor','am','rm'):
			recs = self.env['sos.clients.visit'].search([('date', '>=', date_from), ('date', '<=', date_end),('type', '=', type)], order='date')
		if type == 'all':
			recs = self.env['sos.clients.visit'].search([('date', '>=', date_from), ('date', '<=', date_end)], order='date')

		report = self.env['ir.actions.report']._get_report_from_name('sos.report_clientsvisit')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Visits' :recs or False,
			'get_date_formate' : self.get_date_formate,
		}