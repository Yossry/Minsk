import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class GuardsNoContractReport(models.AbstractModel):
	_name = 'report.sos_payroll.report_guardsnocontract'
	_description = 'Guards Report Having No Contract'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	@api.model
	def _get_report_values(self, docids, data=None):
		emps = self.env['hr.employee'].search([('current','=', True),('is_guard','=',True),('guard_contract_id','=', False)], order='center_id')

		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_guardsnocontract')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			"Employee" : emps or False,
			'get_date_formate' : self.get_date_formate,
		}
		
