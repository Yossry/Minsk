
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp.osv import fields, osv

class invoices_status_by_project(osv.osv_memory):

	_name = 'invoices.status.by.project'
	_description = 'Invoices Status by Project Report'
	_columns = {
		'period_id': fields.many2one('sos.period', string = 'Month'),		
	}
	
	def print_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		
		datas = {'ids': context.get('active_ids', [])}

		res = self.read(cr, uid, ids, context=context)
		res = res and res[0] or {}
		
		datas.update({'form': res})
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'invoices_status_by_project_aeroo',
			'datas': datas,
		}

invoices_status_by_project()

