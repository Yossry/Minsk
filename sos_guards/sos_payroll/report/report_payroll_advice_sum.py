
import time
from datetime import datetime
import pdb
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class guards_payroll_advice_sum_report(report_sxw.rml_parse):
    
	def __init__(self, cr, uid, name, context):
		super(guards_payroll_advice_sum_report, self).__init__(cr, uid, name, context=context)
		
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
		
		result_dict = {}		
		self.total_bysal = 0.00
		
		for l in line_ids:
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
				
			self.total_bysal += round(l.bysal)
			
			
		advances_pool = self.pool.get('sos.advances')
		slip_ids = advances_pool.search(self.cr, self.uid, [('advice_id', '=', advice_id)], context=self.context)
		for adv in advances_pool.browse(self.cr, self.uid, slip_ids, context=self.context):
			result_dict[adv.bankacc]['bysal'] -= adv.amount
			self.total_bysal -= adv.amount
			
		i = 1
		for res_dict in result_dict.items():
			res_dict[1]['serial'] = i
			i = i+1
		
		result = [value for code, value in result_dict.items()]	
		return result

report_sxw.report_sxw('report.payroll.guards.payroll.advice.sum', 'guards.payroll.advice', 'sos/report/report_payroll_advice_sum.rml', parser=guards_payroll_advice_sum_report, header="external")


