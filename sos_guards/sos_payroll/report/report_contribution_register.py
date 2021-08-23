
import time
from datetime import datetime
from dateutil import relativedelta
from odoo.osv import osv
from odoo.report import report_sxw
import pdb

class gcontribution_register_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(gcontribution_register_report, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'get_payslip_lines': self._get_payslip_lines,
			'sum_total': self.sum_total,
		})

	def set_context(self, objects, data, ids, report_type=None):		
		self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
		self.date_to = data['form'].get('date_to', str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
		self.register_id = data['form'].get('register_id')[0]
		return super(gcontribution_register_report, self).set_context(objects, data, ids, report_type=report_type)

	def sum_total(self):
		return self.regi_total

	def _get_payslip_lines(self):
		
		payslip_line = self.pool.get('guards.payslip.line')
		payslip_lines = []
		res = []
		self.regi_total = 0.0
		self.cr.execute("SELECT pl.id from guards_payslip_line as pl "\
						"LEFT JOIN guards_payslip AS hp on (pl.slip_id = hp.id) "\
						"WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "\
						"AND pl.register_id = %s "\
						"AND hp.state = 'done' "\
						"ORDER BY pl.slip_id, pl.sequence",
						(self.date_from, self.date_to, self.register_id))
		payslip_lines = [x[0] for x in self.cr.fetchall()]
		for line in payslip_line.browse(self.cr, self.uid, payslip_lines):
			res.append({
				'employee_name': line.employee_id.code + '/' + line.employee_id.name,
				'post_name': line.post_id.name,
				'total': line.total,
			})
			self.regi_total += line.total
		return res


class wrapped_report_contribution_register(osv.AbstractModel):
    _name = 'report.sos_payroll.report_gcontributionregister'
    _inherit = 'report.abstract_report'
    _template = 'sos_payroll.report_gcontributionregister'
    _wrapped_report_class = gcontribution_register_report
