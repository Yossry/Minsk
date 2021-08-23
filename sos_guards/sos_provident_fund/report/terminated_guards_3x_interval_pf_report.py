import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class TerminatedGuards3XPFReport(models.AbstractModel):
	_name = 'report.sos_provident_fund.terminated_guards_3x_pf_report'
	_description = 'Terminated Guards (3x Interval) PF Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		res = []
		interval_3x_emp_ids = False
		interval_6x_emp_ids = False
		interval_9x_emp_ids = False
		interval_12_emp_ids = False

		interval_3x_total = 0
		interval_6x_total = 0
		interval_9x_total = 0
		interval_12x_total = 0
		grand_total = 0

		interval_3x_emp_ids = self.env['hr.employee'].search([('current', '=', False),('resigdate', '>=', '2019-01-01'),('resigdate', '<=', '2019-03-31')])
		if interval_3x_emp_ids:
			self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
				where pl.code='GPROF' and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" %(tuple(interval_3x_emp_ids.ids),))
			interval_3x_total = self.env.cr.dictfetchall()[0]['total']
			grand_total = grand_total + (interval_3x_total if interval_3x_total is not None else 0)

		interval_6x_emp_ids = self.env['hr.employee'].search([('current', '=', False),('resigdate', '>=', '2019-04-01'),('resigdate', '<=', '2019-06-30')])
		if interval_6x_emp_ids:
			self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
								where pl.code='GPROF' and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" %(tuple(interval_6x_emp_ids.ids),))
			interval_6x_total = self.env.cr.dictfetchall()[0]['total']
			grand_total = grand_total + (interval_6x_total if interval_6x_total is not None else 0)

		interval_9x_emp_ids = self.env['hr.employee'].search([('current', '=', False), ('resigdate', '>=', '2019-07-01'), ('resigdate', '<=', '2019-09-30')])
		if interval_9x_emp_ids:
			self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
								where pl.code='GPROF' and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" %(tuple(interval_9x_emp_ids.ids),))
			interval_9x_total = self.env.cr.dictfetchall()[0]['total']
			grand_total = grand_total + (interval_9x_total if interval_9x_total is not None else 0)

		interval_12x_emp_ids = self.env['hr.employee'].search([('current', '=', False), ('resigdate', '>=', '2019-10-01'), ('resigdate', '<=', '2019-12-31')])
		if interval_12x_emp_ids:
			self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
								where pl.code='GPROF' and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" %(tuple(interval_12x_emp_ids.ids),))
			interval_12x_total = self.env.cr.dictfetchall()[0]['total']
			grand_total = grand_total + (interval_12x_total if interval_12x_total is not None else 0)

		res.append({
			'3x' : interval_3x_total,
			'6x': interval_6x_total,
			'9x': interval_9x_total,
			'12x': interval_12x_total,
			'total' : grand_total,
			'3x_emp' : len(interval_3x_emp_ids),
			'6x_emp': len(interval_6x_emp_ids),
			'9x_emp': len(interval_9x_emp_ids),
			'12x_emp': len(interval_12x_emp_ids),
			})

		report = self.env['ir.actions.report']._get_report_from_name('sos_provident_fund.terminated_guards_3x_pf_report')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			'rep_data' : res,
			"get_date_formate" : self.get_date_formate,
		}