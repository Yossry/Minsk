import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import Warning, RedirectWarning, UserError


class StaffPayrollAdviceSummaryReport(models.AbstractModel):
	_name = 'report.hr_payroll_ext.staff_payroll_advice_summary_report'
	_description = 'HR Advice Summary Report'
	
	def get_date_formate(self,sdate):
		return sdate.strftime('%d %B %Y')
		
	def _get_header_info(self, data=None):
		advice = self.env['hr.payroll.advice'].search([('id','=',data['form']['advice_id'][0])])		
		return {
			'from_date': self.get_date_formate(advice.batch_id.date_start),
			'to_date': self.get_date_formate(advice.batch_id.date_end),
			'bank': advice.bank_id.acc_number,
		}	

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		advice_id = data['form']['advice_id'] and data['form']['advice_id'][0]
		advice = self.env['hr.payroll.advice'].search([('id','=',advice_id)])
		
		result_dict = {}
		total_bysal = 0.00
		
		for l in advice.line_ids:
			code = l.name
			advice_id = l.advice_id.id
			if not code in result_dict:
				result_dict[code] = {					
					'name': l.slip_id.bankacctitle,
					'acc_no': l.slip_id.bankacc,
					'ifsc_code': l.ifsc_code,
					'bysal': round(l.bysal),
					'debit_credit': l.debit_credit,					
				}				
			else:
				result_dict[code]['bysal'] += round(l.bysal)
					
			total_bysal += round(l.bysal)
			
			
		#advances_pool = self.env['sos.advances']
		#slips = advances_pool.search([('advice_id', '=', advice.id)])
		#for adv in slips:
		#	result_dict[adv.bankacc]['bysal'] -= adv.amount
		#	total_bysal -= adv.amount
				
		result = [value for code, value in result_dict.items()]
		report = self.env['ir.actions.report']._get_report_from_name('hr_payroll_ext.staff_payroll_advice_summary_report')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			"Result" : result or False,
			'get_date_formate' : self.get_date_formate,
			'get_header_info': self._get_header_info(data),
			'Total' : total_bysal,
		}