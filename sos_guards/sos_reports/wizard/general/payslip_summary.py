
import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp.osv import fields, osv

class payslip_summary(osv.osv_memory):

	_name = 'payslip.summary'
	_description = 'Payslip Summary Report'
	_columns = {
		'period_id': fields.many2one('sos.period', string = 'From Month'),		
		'period_id2': fields.many2one('sos.period', string = 'To Month'),
		'project_bool': fields.boolean('Include Project Wise Summary in Report'),
		'center_bool': fields.boolean('Include Center Wise Summary in Report'),
	}
	
	_defaults = {
		'project_bool': False,
		'center_bool': False,
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
			'report_name': 'payslips_summary_aeroo',
			'datas': datas,
		}

payslip_summary()

