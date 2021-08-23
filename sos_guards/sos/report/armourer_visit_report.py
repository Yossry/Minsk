import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ArmourerVisitReport(models.AbstractModel):
	_name = 'report.sos.report_armourervisit'
	_description = 'Armourer Visit Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form'):
			raise UserError(_("Form Centent is Missing."))
		
		date_from = data['form']['date_from'] and data['form']['date_from'] 
		date_end= data['form']['date_end'] and data['form']['date_end']
		
		recs = self.env['sos.armourer.visit'].search([('date', '>=', date_from), ('date', '<=', date_end)], order='date')	
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_armourervisit')
		
		return  {
			'doc_ids': self.ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Visits' :recs or False,
			'get_date_formate' : self.get_date_formate,
		}