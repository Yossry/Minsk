import time
import pdb
from datetime import datetime, timedelta
from dateutil import relativedelta
from operator import itemgetter
from odoo import api, fields, models, _
#from odoo.tools import amount_to_text_en


class guards_subadvice_salary_report(models.AbstractModel):
	_name = 'report.sos_payroll.guards_subadvice_salary_report'
	_description = 'Guards Sub Advice Salary Report'
	
	def get_advice(self, form):
		payslip_advice_pool = self.env['guards.payroll.advice']
		if form.get('advice_id',False):
			advice = self.env['guards.payroll.advice'].search([('id','=',form.get('advice_id')[0])])
			return advice    
		else:						
			advice_ids = []
			bankacc = form.get('acc2', '')
			date_from = form.get('date_from', '2013-11-01')
			date_to = form.get('date_to', '2013-11-30')
			
			slip_ids = self.env['guards.payslip'].search([('bankacc','=',bankacc),('date_from','>=',date_from),('date_to','<=',date_to)],order='post_id')
			for slip in slip_ids:
				if slip.advice_id and slip.advice_id.id not in advice_ids:
					advice_ids.append(slip.advice_id.id)
			return payslip_advice_pool.browse(advice_ids)  
			
			    

	def get_slips(self, form):
		advice_id = form.get('advice_id',False)
		if advice_id:
			advice_id = advice_id[0]
		bankacc = form.get('acc', '')
		if bankacc:
			bankacc = bankacc[1]
		
		payslip_advice_pool = self.env['guards.payroll.advice']
		payslip_pool = self.env['guards.payslip']
				
		if advice_id:
			advice_rec = payslip_advice_pool.search([('id','=',advice_id)])
			batch_id = advice_rec.batch_id and advice_rec.batch_id.id or False
			if bankacc:
				slip_ids = payslip_pool.search([('payslip_run_id', '=', batch_id),('bankacc','=',bankacc)],order='post_id')
			else:
				slip_ids = payslip_pool.search([('payslip_run_id', '=', batch_id)],order='post_id')
		else:
			bankacc = form.get('acc2', '')	
			date_from = form.get('date_from', '2013-11-01')
			date_to = form.get('date_to', '2013-11-30')
			
			slip_ids = payslip_pool.search([('bankacc','=',bankacc),('date_from','>=',date_from),('date_to','<=',date_to)], order='post_id')
		return slip_ids
		
	def get_bank(self, form):
		payslip_pool = self.env['guards.payslip']
		advice_id = form.get('advice_id', [])
		if advice_id:
			advice_id = advice_id[0]
		
		accno = form.get('acc', '')
		if	accno:
			accno = accno[1]
				
		res = {
			'accno':	accno and	accno or '', 
			'acctitle': '',
		}
						
		if accno and advice_id:
			slip_ids = payslip_pool.search([('advice_id', '=', advice_id),('bankacc','=', accno)], order='post_id')
		
		elif advice_id:
			slip_ids = payslip_pool.search([('advice_id', '=', advice_id)])
		
		else:
			accno = form.get('acc2', '')
			date_from = form.get('date_from', '2013-11-01')
			date_to = form.get('date_to', '2013-11-30')
			
			res['accno']= accno 
			slip_ids = payslip_pool.search([('bankacc','=',accno),('date_from','>=',date_from),('date_to','<=',date_to)], order='post_id')
		if slip_ids:
			res['acctitle']= slip_ids[0].bankacctitle and slip_ids[0].bankacctitle or ''
			self.acctitle = res['acctitle']	 
		return res 


	def get_month(self, batch_id):
		payslip_run_pool = self.env['guards.payslip.run']
		res = {
			'from_name': '', 'to_name': ''
		}
		run_slip = payslip_run_pool.search([('id','=',batch_id)])		
		from_date = run_slip.date_start
		to_date =  run_slip.date_end
		res['from_name']= from_date.strftime('%d')+'-'+from_date.strftime('%B')+'-'+from_date.strftime('%Y')
		res['to_name']= to_date.strftime('%d')+'-'+to_date.strftime('%B')+'-'+to_date.strftime('%Y')
		return res

	#def convert(self, amount, cur):
	#	return amount_to_text_en.amount_to_text(amount, 'en', cur);

	#def get_bysal_total(self):
	#	return self.total_bysal
        
	def get_attendance_detail(self, emp_id):
		post_pool = self.env['sos.post']
		result = []		
		
		self.env.cr.execute('''SELECT post_id,action,count(*) as cnt FROM sos_guard_attendance WHERE employee_id = %s and name < %s \
			GROUP BY post_id,action''',(emp_id,'2013-09-01'))
		atten = self.env.cr.fetchall()
		for l in atten:
			post = post_pool.search([('id','=',l[0])])
			res = {}
			res.update({
				'postname': post.name,
				'tranaction': l[1],
				'trancnt': l[2],				
			})			
			result.append(res) 
		return result


	def get_slip_detail(self, line_ids):
		result = []		
		for l in line_ids:			
			res = {}
			res.update({
				'postname': l.post_id.name,
				'guard': l.employee_id,
				'trancode': l.code,
				'tranrate': l.rate,
				'tranamount': l.amount,
				'tranquantity': l.quantity,
				'trantotal': l.total,
			})			
			result.append(res) 
		return result

	
	def get_detail(self, line_ids,data):
		result = []
		total_bysal = 0.00
		accno = self.get_bank(data)['accno']
		
		for l in line_ids:
			if not accno or (l.slip_id.bankacc == accno):
				res = {}
				res.update({
					'postname': l.slip_id.post_id.name,
					'name': l.slip_id.employee_id.name,
					'acc_no': l.slip_id.bankacc,
					'ifsc_code': l.ifsc_code,
					'bysal': l.bysal,
					'debit_credit': l.debit_credit,
				})
				total_bysal += l.bysal
				result.append(res)
				
		newlist = sorted(result, key=itemgetter('postname'))
		return newlist,total_bysal
		
	
	@api.model
	def _get_report_values(self, docids, data=None):
		advice_id = data['form']['advice_id'] and data['form']['advice_id'][0] or False
		advice_rec = self.env['guards.payroll.advice'].search([('id','=',advice_id)])
		batch_id = advice_rec.batch_id and advice_rec.batch_id.id or False
		emp_id = False
		line_ids = False
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.guards_subadvice_salary_report')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'get_advice' : self.get_advice,
			'get_bank' : self.get_bank,
			'get_month': self.get_month,
			'get_slips' : self.get_slips,
			'get_attendance_detail' : self.get_attendance_detail,
			'get_slip_detail' : self.get_slip_detail,
			'get_detail' : self.get_detail,
		}