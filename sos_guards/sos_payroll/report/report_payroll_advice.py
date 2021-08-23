import time
from datetime import datetime
import pdb
from odoo.report import report_sxw
from odoo.tools import amount_to_text_en

class guards_payroll_advice_report(report_sxw.rml_parse):
    
	def __init__(self, cr, uid, name, context):
		super(guards_payroll_advice_report, self).__init__(cr, uid, name, context=context)
		
		self.localcontext.update({
			'time': time,
			'get_month': self.get_month,
			'convert': self.convert,
			'get_detail': self.get_detail,
			'get_bysal_total': self.get_bysal_total,
		})
		self.context = context
        
	def get_month(self, batch_id):
		
		payslip_run_pool = self.pool.get('guards.payslip.run')
		res = {
			'from_name': '', 'to_name': ''
		}
				
		run_slip = payslip_run_pool.browse(self.cr, self.uid, [batch_id], context=self.context)[0]
				
		from_date = datetime.strptime(run_slip.date_start, '%Y-%m-%d')
		to_date =  datetime.strptime(run_slip.date_end, '%Y-%m-%d')
				
				
		res['from_name']= from_date.strftime('%d')+'-'+from_date.strftime('%B')+'-'+from_date.strftime('%Y')
		res['to_name']= to_date.strftime('%d')+'-'+to_date.strftime('%B')+'-'+to_date.strftime('%Y')
		
		
		return res

	def convert(self, amount, cur):
		return amount_to_text_en.amount_to_text(amount, 'en', cur);

	def get_bysal_total(self):
		return self.total_bysal
        
	def get_detail(self, line_ids):
		
		result = []
		i = 1
		self.total_bysal = 0.00
		for l in line_ids:
			res = {}
			res.update({
				'serial': i,
				'postname': l.slip_id.post_id.name,
				'name': l.slip_id.employee_id.name,
				'acc_no': l.slip_id.bankacc,
				'ifsc_code': l.ifsc_code,
				'bysal': l.bysal,
				'debit_credit': l.debit_credit,
			})
			i = i + 1
			self.total_bysal += l.bysal
			result.append(res) 
		return result

report_sxw.report_sxw('report.guards.payroll.advice', 'guards.payroll.advice', 'sos/report/report_payroll_advice.rml', parser=guards_payroll_advice_report, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
