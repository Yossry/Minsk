

import time
import pdb
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta


from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
from openerp import tools
from openerp.tools.amount_to_text_en import english_number


class AttrDict(dict):
	"""A dictionary with attribute-style access. It maps attribute access to the real dictionary.  """
	def __init__(self, init={}):
		dict.__init__(self, init)

	def __getstate__(self):
		return self.__dict__.items()

	def __setstate__(self, items):
		for key, val in items:
			self.__dict__[key] = val

	def __repr__(self):
		return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

	def __setitem__(self, key, value):
		return super(AttrDict, self).__setitem__(key, value)

	def __getitem__(self, name):
		item = super(AttrDict, self).__getitem__(name)
		return AttrDict(item) if type(item) == dict else item

	def __delitem__(self, name):
		return super(AttrDict, self).__delitem__(name)

	__getattr__ = __getitem__
	__setattr__ = __setitem__

	def copy(self):
		ch = AttrDict(self)
		return ch


class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.localcontext.update({			
			'amount_in_word': self.amount_in_word,			
			'get_invoices_status_by_project' : self.get_invoices_status_by_project,
			'get_totals': self.get_totals,
			'get_serial': self.get_serial,
			'get_byprj_total': self.get_byprj_total,
			'get_projects': self.get_projects,
			'get_centers': self.get_centers,
			'get_posts': self.get_posts,
			'get_invoices_summary': self.get_invoices_summary,
			'get_invoices_summary_project': self.get_invoices_summary_project,
			'get_invoices_summary_center': self.get_invoices_summary_center,
			'get_payslips_summary': self.get_payslips_summary,
			'get_payslips_summary_project': self.get_payslips_summary_project,
			'get_payslips_summary_center': self.get_payslips_summary_center,
			'get_acc_bal': self.get_acc_bal,
			'get_bal_by_ac': self.get_bal_by_ac,
			'get_bal': self.get_bal,
			'get_period': self.get_period,
			'set_period': self.set_period,
			'set_period_id': self.set_period_id,
			'set_analysis_period': self.set_analysis_period,
			'get_center_bal': self.get_center_bal,
			'get_center_rev': self.get_center_rev,
			'get_center_guard_sal': self.get_center_guard_sal,
			'get_center_emp_sal': self.get_center_emp_sal,
			'get_guards_payslips_payable_project': self.get_guards_payslips_payable_project,
			'get_project_bank_sal': self.get_project_bank_sal,
			'get_post_invoice_salary_detail': self.get_post_invoice_salary_detail,
			'get_invoices_status_by_center':self.get_invoices_status_by_center,
			'get_invoices_status_by_post':self.get_invoices_status_by_post,
			'get_invoices_comp_summary_projects': self.get_invoices_comp_summary_projects,
			'get_invoices_comp_summary_centers': self.get_invoices_comp_summary_centers,
			'get_invoices_comp_summary_posts': self.get_invoices_comp_summary_posts,
			'get_profitability_by_center': self.get_profitability_by_center,
			'get_profitability_by_project': self.get_profitability_by_project,
			'get_salary_comp_summary_centers': self.get_salary_comp_summary_centers,
			'get_salary_comp_summary_projects': self.get_salary_comp_summary_projects,
			'get_salary_comp_summary_posts': self.get_salary_comp_summary_posts,
			'get_gst_summary_centers': self.get_gst_summary_centers,
			'get_gst_summary_projects': self.get_gst_summary_projects,
			'get_gst_summary_posts': self.get_gst_summary_posts,
			'get_gst_summary_percentage': self.get_gst_summary_percentage,
			'get_common_summary_projects': self.get_common_summary_projects,
			'get_common_summary_centers': self.get_common_summary_centers,
			'get_shortfall_summary_posts': self.get_shortfall_summary_posts,
			'get_tax_summary_posts': self.get_tax_summary_posts,
			'get_penalty_summary_posts': self.get_penalty_summary_posts,
			'get_bankcharges_summary_posts': self.get_bankcharges_summary_posts,
			'get_post_invoices': self.get_post_invoices,
		})
		self.totals = AttrDict({'serial':0,'saldays':0,'saltotal':0,'invdays':0,'invtotal':0,'current_total':0,'prev_total':0,'diff_total':0,'invoiced':0,'credit_note':0,'net_invoiced':0,'salary':0,'gross':0,'shortfall':0,'taxed':0,'withheld':0,'pending':0,'received':0,'tax':0,'penalty':0,'bankcharges':0})
			
	def amount_in_word(self, amount_total):
		number = '%.2f' % amount_total
		units_name = 'PKR'
		list = str(number).split('.')
		start_word = english_number(int(list[0]))
		return ' '.join(filter(None, [start_word, units_name]))
		
		
	def get_serial(self):
		self.totals.serial = self.totals.serial+1
		return self.totals.serial
		
	def get_post_invoice_salary_detail(self, project,form):
		result = []
		self.total_byprj = {}
		date_from = form.get('date_from', '2013-10-01')
		date_to = form.get('date_to', '2013-10-31')
		target_move = form.get('target_move', 'all')
			
			
		for post in project.post_ids:

			if project.id == 30:
				date_from = str(datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=1))[:10]
				date_to = str(datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=-1,day=31))[:10]	

			self.cr.execute('''SELECT sum(quantity) qty ,sum(gpl.total) tot from guards_payslip gp ,guards_payslip_line gpl \
				where gp.id = gpl.slip_id and code = 'BASIC' and gpl.post_id = %s and gp.date_from >= %s and gp.date_to <= %s''',(post.id,date_from,date_to))
			salary = self.cr.fetchall()

			if project.id in (30,32):
				date_from = str(datetime.strptime(date_from,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=1))[:10]
				date_to = str(datetime.strptime(date_to,'%Y-%m-%d')+relativedelta.relativedelta(months=+1,day=31))[:10]	

			self.cr.execute('''SELECT sum(quantity) qty ,sum(price_subtotal) tot from account_invoice acinv ,account_invoice_line acinvl \
				where acinv.id = acinvl.invoice_id and acinv.post_id = %s and move_id is not NULL and date_invoice between %s and %s''',(post.id,date_from,date_to))

			invoice = self.cr.fetchall()
				
			if target_move == 'all' or (target_move == 'diff' and salary[0][0] != invoice[0][0]) or (target_move == 'more' and salary[0][0] > invoice[0][0])  or (target_move == 'less' and salary[0][0] < invoice[0][0]):

				res = {}
				saldays = salary[0][0] or 0
				saltotal = salary[0][1] or 0
				invdays = invoice[0][0] or 0
				invtotal = invoice[0][1] or 0
				
				res.update({
					'name': post.name,
					'saldays': saldays,
					'saltotal': saltotal,	
					'invdays': invdays,
					'invtotal': invtotal,
					'diff': invdays - saldays, 
					
				})			

				result.append(res) 			


		self.total_byprj.update({
			'saldays': reduce(lambda x, obj: x + obj['saldays'], result, 0),
			'saltotal': reduce(lambda x, obj: x + obj['saltotal'], result, 0),
			'invdays': reduce(lambda x, obj: x + obj['invdays'], result, 0),
			'invtotal': reduce(lambda x, obj: x + obj['invtotal'], result, 0),
		})

		self.totals.update({
			'saldays': self.totals['saldays'] + self.total_byprj['saldays'],
			'saltotal': self.totals['saltotal'] + self.total_byprj['saltotal'],
			'invdays': self.totals['invdays'] + self.total_byprj['invdays'],
			'invtotal': self.totals['invtotal'] + self.total_byprj['invtotal'],
		})
			
		return result
	
	def set_period_id(self,period_id):
		period_obj = self.pool.get('sos.period')
				
		self.period_id = period_id	

		period_to = period_obj.browse(self.cr,self.uid,self.period_id).name
		return period_to
	
	def set_analysis_period(self,date_to):
		period_obj = self.pool.get('sos.period')
				
		date_from =  str(datetime.strptime(date_to, "%Y-%m-%d") + relativedelta.relativedelta(months=-2, day=31))[:10]
		period_ids = period_obj.find(self.cr, self.uid, dt=date_from)
		self.period_from = period_ids[0]				
		
		date_medium =  str(datetime.strptime(date_to, "%Y-%m-%d") + relativedelta.relativedelta(months=-1, day=31))[:10]
		period_ids = period_obj.find(self.cr, self.uid, dt=date_medium)
		self.period_medium = period_ids[0]						
		
		period_ids = period_obj.find(self.cr, self.uid, dt=date_to)
		self.period_to = period_ids[0]	
		
		period_from = period_obj.browse(self.cr,self.uid,self.period_from).name
		period_to = period_obj.browse(self.cr,self.uid,self.period_to).name
		period_medium = period_obj.browse(self.cr,self.uid,self.period_medium).name
		
		self.totals = AttrDict({'from':period_from, 'to':period_to, 'medium':period_medium})	
		
		return period_from + ' to ' + period_to
	
	def get_center_rev(self, center_id, diff):
		acc_obj = self.pool.get('account.account')
		acc_id = 13265
		
		if diff == 1:
			period_id = self.period_from
		if diff == 2:
			period_id = self.period_medium
		if diff == 3:
			period_id = self.period_to
				
		
		data1 = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and center_id = %s and journal_id = %s",query_params=(period_id,center_id,1))
		data2 = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and center_id = %s and journal_id = %s",query_params=(period_id,center_id,3))
		return data1[acc_id]['credit'] - data2[acc_id]['debit']

	def get_center_guard_sal(self, center_id, diff):
		acc_obj = self.pool.get('account.account')
		acc_id = 13266

		if diff == 1:
			period_id = self.period_from
		if diff == 2:
			period_id = self.period_medium
		if diff == 3:
			period_id = self.period_to


		data1 = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and center_id = %s",query_params=(period_id,center_id))
		return data1[acc_id]['debit']
	
	def get_center_emp_sal(self, center_id, diff):
		acc_obj = self.pool.get('account.account')
		acc_id = 11833

		if diff == 1:
			period_id = self.period_from
		if diff == 2:
			period_id = self.period_medium
		if diff == 3:
			period_id = self.period_to


		data1 = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and center_id = %s",query_params=(period_id,center_id))
		return data1[acc_id]['debit']
	
	def get_center_bal(self,acc_id,center_id,date_from, diff):
		acc_obj = self.pool.get('account.account')
		period_obj = self.pool.get('sos.period')
						
		date_from =  str(datetime.strptime(date_from, "%Y-%m-%d") + relativedelta.relativedelta(months=diff, day=31))[:10]
				
		period_ids = period_obj.find(self.cr, self.uid, dt=date_from)
		period_id = period_ids[0]				
		
				
		data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and center_id = %s",query_params=(period_id,center_id))
		return {
			'balance': data[acc_id]['balance'],
			'debit': data[acc_id]['debit'],
			'credit': data[acc_id]['credit'],
		}
	
	def get_period(self,period_id):
		period_obj = self.pool.get('sos.period')
		period = period_obj.browse(self.cr, self.uid, period_id)
			
		return period
	
	def set_period(self,date_from,date_to,period=False,opening=True):
		period_ids = self.pool.get('sos.period').find(self.cr, self.uid, dt=date_from)
		self.period_from = period_ids[0]
		
		period_ids = self.pool.get('sos.period').find(self.cr, self.uid, dt=date_to)
		self.period_to = period_ids[0]
		
		self.date_from = date_from
		self.date_to = date_to
		self.period = period
		self.opening = opening
		
		return date_from+' to '+date_to
	
	def get_acc_bal(self,acc_id):
		acc_obj = self.pool.get('account.account')
		
		if self.period:
			odata = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance'],query="period_id < %s and period_id < %s and move_id <> 74839",query_params=(self.period_from,self.period_to))
			data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['debit','credit'],query="period_id between %s and %s and move_id <> 74839",query_params=(self.period_from,self.period_to))
		else:
			odata = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance'],query="date < %s and date < %s and move_id <> 74839",query_params=(self.date_from,self.date_to))
			data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['debit','credit'],query="date between %s and %s and move_id <> 74839",query_params=(self.date_from,self.date_to))
		
		return {
			'balance': self.opening and odata[acc_id]['balance'] or 0,
			'debit': data[acc_id]['debit'],
			'credit': data[acc_id]['credit'],
		}
	
	def get_project_bank_sal(self,acc_no,project_id = False):
		acc_obj = self.pool.get('account.account')
		
		acc_id = acc_obj.search(self.cr,self.uid,[('code','=',acc_no)])
		if acc_id:
			acc_id = acc_id[0]
			data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and project_id = %s",query_params=(self.period_id,project_id))
			return {
				'balance': data[acc_id]['balance'],
				'debit': data[acc_id]['debit'],
				'credit': data[acc_id]['credit'],
			}	
		else:
			return {
				'balance': 0,
				'debit': 0,
				'credit': 0,
		}	
	
	def get_bal_by_ac(self,acc_no,diff,center_id = False):
		acc_obj = self.pool.get('account.account')
	
		if diff == 1:
			period_id = self.period_from
		if diff == 2:
			period_id = self.period_medium
		if diff == 3:
			period_id = self.period_to
	
		acc_id = acc_obj.search(self.cr,self.uid,[('code','=',acc_no)])
		if acc_id:
			acc_id = acc_id[0]
			data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id = %s and company_id = %s",query_params=(period_id,1))
			return {
				'balance': data[acc_id]['balance'],
				'debit': data[acc_id]['debit'],
				'credit': data[acc_id]['credit'],
			}	
		else:
			return {
				'balance': 0,
				'debit': 0,
				'credit': 0,
			}	
	
	def get_bal(self,acc_id,center_id = False):
		acc_obj = self.pool.get('account.account')

		data = acc_obj.compute_bal(self.cr,self.uid, [acc_id],['balance','debit','credit'],query="period_id between %s and %s",query_params=(self.period_from,self.period_to))
		return {
			'balance': data[acc_id]['balance'],
			'debit': data[acc_id]['debit'],
			'credit': data[acc_id]['credit'],
		}
		
	def get_invoices_status_by_project(self, data):
		date_from = data['date_from']
		date_to = data['date_to']	
		invoice_obj = self.pool.get('account.invoice')
		self.totals = AttrDict({'amount_taxed':0,'amount_untaxed':0,'amount_insurance':0,'amount_shortfall':0,'amount_fine':0,'amount_tax':0,'amount_writeoff':0,
			'amount_gst':0,'bankcharges':0,'amount_total':0,'amount_credit':0,'bad_debits':0,'paidon':0,'residual':0,'received':0})
		
		project_obj = self.pool.get('sos.project')
		ids = project_obj.search(self.cr,self.uid,[])
		projects = project_obj.browse(self.cr,self.uid,ids)
		res = []
		
		for project in projects:
			
			self.cr.execute("select sum(debit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13262 and \
				aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			invoiced = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13265 and \
				aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			untaxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13535 and \
				aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			insurance = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 and \
				aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			taxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(residual) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and project_id = %s and journal_id = 1",(date_from,date_to,project.id))
			residual = self.cr.dictfetchall()[0]	
						
			
			self.cr.execute("select sum(amount_total) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and project_id = %s and journal_id = 3",(date_from,date_to,project.id))
			credit_note = self.cr.dictfetchall()[0]
			
						
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.move_id = aml.move_id and aml.account_id = 13263 and \
				aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			paid_on = self.cr.dictfetchall()[0]
						
			received = 0
			shortfall = 0
			fine = 0
			gst = 0
			tax = 0
			bankcharges = 0
			paidon = 0
			writeoff = 0
			
			#invoice_ids = invoice_obj.search(self.cr,self.uid,[('date_invoice','>=',date_from),('date_invoice','<=',date_to),('project_id','=',project.id)])
			#for invoice in invoice_obj.browse(self.cr,self.uid,invoice_ids):
			#	for payment in invoice.payment_ids:
			#		if payment.journal_id.type in ('bank','cash'):
			#			received = received + payment.credit		
			#		elif payment.journal_id.id == 29:
			#			shortfall = shortfall + payment.credit
			#		elif payment.journal_id.id == 31:
			#			fine = fine + payment.credit
			#		elif payment.journal_id.id == 32:
			#			gst = gst + payment.credit
			#		elif payment.journal_id.id == 30:
			#			tax = tax + payment.credit	
			#		elif payment.journal_id.id == 35:
			#			bankcharges = bankcharges + payment.credit
			#		elif payment.journal_id.id == 37:
			#			writeoff = writeoff + payment.credit
			#		elif payment.journal_id.id == 23:
			#			paidon = paidon + payment.credit
			#		elif payment.journal_id.id == 1:
			#			continue
					
						
			res.append({
				'name': project.name,
				'amount_taxed': int(taxed['amount'] or 0) or '-',
				'amount_untaxed': int(untaxed['amount'] or 0) or '-',
				'amount_total': int(invoiced['amount'] or 0) or '-',
				
				'amount_insurance': int(insurance['amount'] or 0) or '-',
				'amount_credit': int(credit_note['amount'] or 0) or '-',
				'residual': int(residual['amount'] or 0) or '-',
				'received': received,
				'amount_shortfall': shortfall,
				'amount_fine': fine,
				'amount_gst': gst,
				'amount_tax': tax,
				'amount_writeoff': writeoff,
				'bankcharges': bankcharges,
				'paidon': paidon,
				
			})
			self.totals.amount_taxed += int(taxed['amount'] or 0)
			self.totals.amount_untaxed += int(untaxed['amount'] or 0)
			self.totals.amount_insurance += int(insurance['amount'] or 0)
			self.totals.amount_total += int(invoiced['amount'] or 0)
			self.totals.residual += int(residual['amount'] or 0)
			
			self.totals.amount_shortfall += shortfall
			self.totals.amount_fine += fine
			self.totals.amount_gst += gst
			self.totals.amount_tax += tax
			self.totals.bankcharges += bankcharges
			self.totals.amount_writeoff += writeoff
			self.totals.amount_credit += int(credit_note['amount'] or 0)
			self.totals.paidon += paidon
			
			self.totals.received += received
		return res
		
		
	def get_invoices_status_by_center(self, data):
		date_from = data['date_from']
		date_to = data['date_to']		
		invoice_obj = self.pool.get('account.invoice')
		self.totals = AttrDict({'amount_taxed':0,'amount_untaxed':0,'amount_insurance':0,'amount_shortfall':0,'amount_fine':0,'amount_tax':0,'amount_writeoff':0,
			'amount_gst':0,'bankcharges':0,'amount_total':0,'amount_credit':0,'bad_debits':0,'paidon':0,'residual':0,'received':0})
		
		center_obj = self.pool.get('sos.center')
		ids = center_obj.search(self.cr,self.uid,[])
		centers = center_obj.browse(self.cr,self.uid,ids)
		res = []
		
		for center in centers:
			
			self.cr.execute("select sum(debit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13262 and \
				aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			invoiced = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13265 and \
				aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			untaxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13535 and \
				aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			insurance = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 and \
				aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			taxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(residual) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and journal_id = 1",(date_from,date_to,center.id))
			residual = self.cr.dictfetchall()[0]	
						
			
			self.cr.execute("select sum(amount_total) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and journal_id = 3",(date_from,date_to,center.id))
			credit_note = self.cr.dictfetchall()[0]
			
						
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.move_id = aml.move_id and aml.account_id = 13263 and \
				aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			paid_on = self.cr.dictfetchall()[0]
						
			received = 0
			shortfall = 0
			fine = 0
			gst = 0
			tax = 0
			bankcharges = 0
			paidon = 0
			writeoff = 0
			
			#invoice_ids = invoice_obj.search(self.cr,self.uid,[('period_id','=',prid),('center_id','=',center.id)])
			#for invoice in invoice_obj.browse(self.cr,self.uid,invoice_ids):
			#	for payment in invoice.payment_ids:
			#		if payment.journal_id.type in ('bank','cash'):
			#			received = received + payment.credit		
			#		elif payment.journal_id.id == 29:
			#			shortfall = shortfall + payment.credit
			#		elif payment.journal_id.id == 31:
			#			fine = fine + payment.credit
			#		elif payment.journal_id.id == 32:
			#			gst = gst + payment.credit
			#		elif payment.journal_id.id == 30:
			#			tax = tax + payment.credit	
			#		elif payment.journal_id.id == 35:
			#			bankcharges = bankcharges + payment.credit
			#		elif payment.journal_id.id == 37:
			#			writeoff = writeoff + payment.credit
			#		elif payment.journal_id.id == 23:
			#			paidon = paidon + payment.credit
			#		elif payment.journal_id.id == 1:
			#			continue
			
			int(taxed['amount'] or 0) or '-',		
						
			res.append({
				'name': center.name,
				'amount_taxed': int(taxed['amount'] or 0) or '-',
				'amount_untaxed': int(untaxed['amount'] or 0) or '-',
				'amount_total': int(invoiced['amount'] or 0) or '-',
				
				'amount_insurance': int(insurance['amount'] or 0) or '-',
				'amount_credit': int(credit_note['amount'] or 0) or '-',
				'residual': int(residual['amount'] or 0) or '-',
				'received': received,
				'amount_shortfall': shortfall,
				'amount_fine': fine,
				'amount_gst': gst,
				'amount_tax': tax,
				'amount_writeoff': writeoff,
				'bankcharges': bankcharges,
				'paidon': paidon,
				
			})
			self.totals.amount_taxed += int(taxed['amount'] or 0)
			self.totals.amount_untaxed += int(untaxed['amount'] or 0)
			self.totals.amount_insurance += int(insurance['amount'] or 0)
			self.totals.amount_total += int(invoiced['amount'] or 0)
			self.totals.residual += int(residual['amount'] or 0)
			
			self.totals.amount_shortfall += shortfall
			self.totals.amount_fine += fine
			self.totals.amount_gst += gst
			self.totals.amount_tax += tax
			self.totals.bankcharges += bankcharges
			self.totals.amount_writeoff += writeoff
			self.totals.amount_credit += int(credit_note['amount'] or 0)
			self.totals.paidon += paidon
			
			self.totals.received += received
		return res
		
		
	def get_invoices_status_by_post(self, data):
		date_from = data['date_from']
		date_to = data['date_to']	
		invoice_obj = self.pool.get('account.invoice')
		self.totals = AttrDict({'amount_taxed':0,'amount_untaxed':0,'amount_insurance':0,'amount_shortfall':0,'amount_fine':0,'amount_tax':0,'amount_writeoff':0,'amount_gst':0,'bankcharges':0,'amount_total':0,'amount_credit':0,'bad_debits':0,'paidon':0,'residual':0,'received':0})
		
		post_obj = self.pool.get('sos.post')
		ids = post_obj.search(self.cr,self.uid,[])
		posts = post_obj.browse(self.cr,self.uid,ids)
		res = []
		
		for post in posts:
			
			self.cr.execute("select sum(debit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13262 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			invoiced = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13265 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			untaxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13535 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			insurance = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			taxed = self.cr.dictfetchall()[0]
			
			self.cr.execute("select sum(residual) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and post_id = %s and journal_id = 1",(date_from,date_to,post.id))
			residual = self.cr.dictfetchall()[0]	
						
			
			self.cr.execute("select sum(amount_total) as amount from \
				account_invoice where date_invoice >= %s and date_invoice <= %s and post_id = %s and journal_id = 3",(date_from,date_to,post.id))
			credit_note = self.cr.dictfetchall()[0]
			
						
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.move_id = aml.move_id and aml.account_id = 13263 and \
				aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			paid_on = self.cr.dictfetchall()[0]
						
			received = 0
			shortfall = 0
			fine = 0
			gst = 0
			tax = 0
			bankcharges = 0
			paidon = 0
			writeoff = 0
			
			#invoice_ids = invoice_obj.search(self.cr,self.uid,[('period_id','=',prid),('post_id','=',post.id)])
			#for invoice in invoice_obj.browse(self.cr,self.uid,invoice_ids):
			#	for payment in invoice.payment_ids:
			#		if payment.journal_id.type in ('bank','cash'):
			#			received = received + payment.credit		
			#		elif payment.journal_id.id == 29:
			#			shortfall = shortfall + payment.credit
			#		elif payment.journal_id.id == 31:
			#			fine = fine + payment.credit
			#		elif payment.journal_id.id == 32:
			#			gst = gst + payment.credit
			#		elif payment.journal_id.id == 30:
			#			tax = tax + payment.credit	
			#		elif payment.journal_id.id == 35:
			#			bankcharges = bankcharges + payment.credit
			#		elif payment.journal_id.id == 37:
			#			writeoff = writeoff + payment.credit
			#		elif payment.journal_id.id == 23:
			#			paidon = paidon + payment.credit
			#		elif payment.journal_id.id == 1:
			#			continue
					
						
			res.append({
				'name': post.name,
				'amount_taxed': int(taxed['amount'] or 0) or '-',
				'amount_untaxed': int(untaxed['amount'] or 0) or '-',
				'amount_total': int(invoiced['amount'] or 0) or '-',
				
				'amount_insurance': int(insurance['amount'] or 0) or '-',
				'amount_credit': int(credit_note['amount'] or 0) or '-',
				'residual': int(residual['amount'] or 0) or '-',
				'received': received,
				'amount_shortfall': shortfall,
				'amount_fine': fine,
				'amount_gst': gst,
				'amount_tax': tax,
				'amount_writeoff': writeoff,
				'bankcharges': bankcharges,
				'paidon': paidon,
				
			})
			self.totals.amount_taxed += int(taxed['amount'] or 0)
			self.totals.amount_untaxed += int(untaxed['amount'] or 0)
			self.totals.amount_insurance += int(insurance['amount'] or 0)
			self.totals.amount_total += int(invoiced['amount'] or 0)
			self.totals.residual += int(residual['amount'] or 0)
			
			self.totals.amount_shortfall += shortfall
			self.totals.amount_fine += fine
			self.totals.amount_gst += gst
			self.totals.amount_tax += tax
			self.totals.bankcharges += bankcharges
			self.totals.amount_writeoff += writeoff
			self.totals.amount_credit += int(credit_note['amount'] or 0)
			self.totals.paidon += paidon
			
			self.totals.received += received
		return res
	
	def get_invoices_summary(self,prid,prid2):
		period_obj = self.pool.get('sos.period')	
		invoice_obj = self.pool.get('account.invoice')
		
		self.totals = AttrDict({'diff':0})
		res = []
		
		self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,1))
		data = self.cr.dictfetchall()[0]	

		self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,3))
		credit_note = self.cr.dictfetchall()[0]
		
		prev_amount = data['amount_untaxed'] - int(0 if credit_note['amount_total'] is None else credit_note['amount_total']) 
				
		while prid <= prid2:  
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and journal_id = %s and state in ('open','paid')",(prid,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and journal_id = %s and state in ('open','paid')",(prid,3))
			credit_note = self.cr.dictfetchall()[0]
			
			amount = data['amount_untaxed'] - int(0 if credit_note['amount_total'] is None else credit_note['amount_total']) 
			diff = amount-prev_amount
			
			period = period_obj.browse(self.cr,self.uid,prid)
						
			res.append({
				'period_name': period.name,
				'amount_untaxed': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})
			
			self.totals.diff += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
			
		return res
	
	def get_centers(self,center_ids=False):
		center_obj = self.pool.get('sos.center')
		
		if not center_ids:
			center_ids = center_obj.search(self.cr,self.uid,[])
		
		centers = center_obj.browse(self.cr,self.uid,center_ids)
		return centers
	
	
	def get_projects(self,project_ids=False):
		project_obj = self.pool.get('sos.project')
		
		if not project_ids:		
			project_ids = project_obj.search(self.cr,self.uid, [])
		
		projects = project_obj.browse(self.cr,self.uid,project_ids)
		return projects
	
	def get_posts(self,project_id=False,center_id=False):
		post_obj = self.pool.get('sos.post')
		rec_domain = []
		if project_id:
			rec_domain.append(['project_id','=',project_id])
		if center_id:
			rec_domain.append(['center_id','=',center_id])
			
		post_ids = post_obj.search(self.cr, self.uid, rec_domain)	
		return post_obj.browse(self.cr,self.uid,post_ids)
		
	def get_post_invoices(self, post_id):
		invoice_obj = self.pool.get('account.invoice')
		invoice_ids = invoice_obj.search(self.cr,self.uid, [('post_id','=',post_id)],order = 'date_from')
				
		invoices = invoice_obj.browse(self.cr,self.uid,invoice_ids)
		return invoices
	
	def get_invoices_summary_project(self,prid,prid2,project):
		period_obj = self.pool.get('sos.period')	
		
		self.totals = AttrDict({'diffprj':0})
		res = []
		
		self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,project,1))
		data = self.cr.dictfetchall()[0]	

		self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,project, 3))
		credit_note = self.cr.dictfetchall()[0]
		prev_amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])

		while prid <= prid2:  
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid,project,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid,project,3))
			credit_note = self.cr.dictfetchall()[0]

			amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
			diff = amount-prev_amount
			
			period = period_obj.browse(self.cr,self.uid,prid)
			
			res.append({
				'period_name': period.name,
				'amount_untaxed': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.diffprj += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
				
		return res
		
	def get_invoices_comp_summary_projects(self,data):
		prid = data['period_id'][0]
		projects = self.get_projects(False)
				
		res = []
		
		for project in projects:
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,project.id,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,project.id, 3))
			credit_note = self.cr.dictfetchall()[0]
			prev_amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
	
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid,project.id,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and project_id = %s and journal_id = %s and state in ('open','paid')",(prid,project.id,3))
			credit_note = self.cr.dictfetchall()[0]
			amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])

			diff = amount-prev_amount
				
			res.append({
				'project_name': project.name,
				'amount': amount or '-',
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})
			
			self.totals.prev_total += int(0 if prev_amount is None else prev_amount)
			self.totals.current_total += int(0 if amount is None else amount)
			self.totals.diff_total += int(0 if diff is None else diff)
						
		return res
	
	def get_invoices_summary_center(self,prid,prid2,center_id):
		period_obj = self.pool.get('sos.period')	
		invoice_obj = self.pool.get('account.invoice')

		self.totals = AttrDict({'diffcnt':0})
		res = []

		self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,center_id,1))
		data = self.cr.dictfetchall()[0]	

		self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,center_id, 3))
		credit_note = self.cr.dictfetchall()[0]
		prev_amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])

		while prid <= prid2:  
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid,center_id,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid,center_id,3))
			credit_note = self.cr.dictfetchall()[0]

			amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
			diff = amount-prev_amount

			period = period_obj.browse(self.cr,self.uid,prid)

			res.append({
				'period_name': period.name,
				'amount_untaxed': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.diffcnt += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
					
		return res
	
	def get_invoices_comp_summary_centers(self,data):
		prid = data['period_id'][0]
		centers = self.get_centers(False)

		res = []

		for center in centers:
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,center.id,1))
			data = self.cr.dictfetchall()[0]	
			
			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,center.id, 3))
			credit_note = self.cr.dictfetchall()[0]
			prev_amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])

			
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid,center.id,1))
			data = self.cr.dictfetchall()[0]	
			
			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and center_id = %s and journal_id = %s and state in ('open','paid')",(prid,center.id,3))
			credit_note = self.cr.dictfetchall()[0]
			
			amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
			diff = amount-prev_amount
			
			res.append({
				'center_name': center.name,
				'amount': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.prev_total += int(0 if prev_amount is None else prev_amount)
			self.totals.current_total += int(0 if amount is None else amount)
			self.totals.diff_total += int(0 if diff is None else diff)
							
		return res
	
	def get_salary_comp_summary_centers(self,data):
		prid = data['period_id'][0]
		centers = self.get_centers(False)

		res = []

		for center in centers:
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.center_id = %s and code = %s and state in ('done')",(prid-1,center.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			prev_salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
			
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.center_id = %s and code = %s and state in ('done')",(prid,center.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
			
			
			diff = salary-prev_salary

			res.append({
				'center_name': center.name,
				'amount': salary,
				'amount_prev': prev_salary or '-',
				'diff': diff or '-',
			})

			self.totals.prev_total += prev_salary
			self.totals.current_total += salary
			self.totals.diff_total += diff
								
		return res
	
	def get_salary_comp_summary_projects(self,data):
		prid = data['period_id'][0]
		projects = self.get_projects(False)

		res = []

		for project in projects:
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.project_id = %s and code = %s and state in ('done')",(prid-1,project.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			prev_salary = int(0 if salary_data['amount'] is None else salary_data['amount'])

			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.project_id = %s and code = %s and state in ('done')",(prid,project.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			salary = int(0 if salary_data['amount'] is None else salary_data['amount'])


			diff = salary-prev_salary

			res.append({
				'project_name': project.name,
				'amount': salary,
				'amount_prev': prev_salary or '-',
				'diff': diff or '-',
			})

			self.totals.prev_total += prev_salary
			self.totals.current_total += salary
			self.totals.diff_total += diff
									
		return res
		
	def get_salary_comp_summary_posts(self,data,center_id,project_id):
		prid = data['period_id'][0]

		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)

		res = []

		for post in posts:

			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.post_id = %s and code = %s and state in ('done')",(prid-1,post.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			prev_salary = int(0 if salary_data['amount'] is None else salary_data['amount'])

			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.post_id = %s and code = %s and state in ('done')",(prid,post.id,'BASIC'))
			salary_data = self.cr.dictfetchall()[0]
			salary = int(0 if salary_data['amount'] is None else salary_data['amount'])
			
			diff = salary-prev_salary
			
			res.append({
				'post_name': post.name,
				'amount': salary,
				'amount_prev': prev_salary or '-',
				'diff': diff or '-',
			})

			self.totals.prev_total += prev_salary
			self.totals.current_total += salary
			self.totals.diff_total += diff
									
		return res
	
	def get_gst_summary_projects(self,data):
		date_from = data['date_from']
		date_to = data['date_to']
		projects = self.get_projects(False)

		res = []

		for project in projects:
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			taxed_data = self.cr.dictfetchall()[0]
			taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 32 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			withheld_data = self.cr.dictfetchall()[0]
			withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			received_data = self.cr.dictfetchall()[0]
			received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			pending_data = self.cr.dictfetchall()[0]
			pending = int(0 if pending_data['amount'] is None else pending_data['amount']) 

			res.append({
				'project_name': project.name,
				'taxed': taxed or '-',
				'withheld': withheld or '-',
				'pending': pending or '-',
				'received': received or '-',				
			})

			self.totals.taxed += taxed
			self.totals.withheld += withheld
			self.totals.pending += pending
			self.totals.received += received
				
		return res
		
	def get_gst_summary_centers(self,data):
		date_from = data['date_from']
		date_to = data['date_to']

		centers = self.get_centers(False)
		
		res = []

		for center in centers:
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			taxed_data = self.cr.dictfetchall()[0]
			taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 32 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			withheld_data = self.cr.dictfetchall()[0]
			withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			received_data = self.cr.dictfetchall()[0]
			received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			pending_data = self.cr.dictfetchall()[0]
			pending = int(0 if pending_data['amount'] is None else pending_data['amount']) 
			
			res.append({
				'center_name': center.name,
				'taxed': taxed or '-',
				'withheld': withheld or '-',
				'pending': pending or '-',
				'received': received or '-',				
			})

			self.totals.taxed += taxed
			self.totals.withheld += withheld
			self.totals.pending += pending
			self.totals.received += received
			
		return res
	
	def get_gst_summary_posts(self,data,center_id,project_id):
		date_from = data['date_from']
		date_to = data['date_to']
				
		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)
				
		res = []

		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			taxed_data = self.cr.dictfetchall()[0]
			taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 32 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			withheld_data = self.cr.dictfetchall()[0]
			withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			received_data = self.cr.dictfetchall()[0]
			received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			pending_data = self.cr.dictfetchall()[0]
			pending = int(0 if pending_data['amount'] is None else pending_data['amount']) 
			
			res.append({
				'post_name': post.name,
				'taxed': taxed or '-',
				'withheld': withheld or '-',
				'pending': pending or '-',
				'received': received or '-',				
			})

			self.totals.taxed += taxed
			self.totals.withheld += withheld
			self.totals.pending += pending
			self.totals.received += received
									
		return res
	
	def get_gst_summary_percentage(self,data):
		date_from = data['date_from']
		date_to = data['date_to']
		percentage = data['percentage'][0]

		post_ids = []
		
		self.cr.execute("select distinct ai.post_id from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = %s and \
			and aml.date >= %s and aml.date <= %s and invoice_line_tax_id = %s",(13488,date_from,date_to,percentage))
		data_posts = self.cr.dictfetchall()
		for post in data_posts:
			post_ids.append(post['post_id'])
			
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)	
		res = []
	
		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and invoice_line_tax_id = %s",(date_from,date_to,post.id,percentage))
			taxed_data = self.cr.dictfetchall()[0]
			taxed = int(0 if taxed_data['amount'] is None else taxed_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 32 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and invoice_line_tax_id = %s",(date_from,date_to,post.id,percentage))
			withheld_data = self.cr.dictfetchall()[0]
			withheld = int(0 if withheld_data['amount'] is None else withheld_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='paid' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and invoice_line_tax_id = %s",(date_from,date_to,post.id,percentage))
			received_data = self.cr.dictfetchall()[0]
			received = int(0 if received_data['amount'] is None else received_data['amount']) - withheld

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and ai.state='open' and aml.account_id = 13488 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s and invoice_line_tax_id = %s",(date_from,date_to,post.id,percentage))
			pending_data = self.cr.dictfetchall()[0]
			pending = int(0 if pending_data['amount'] is None else pending_data['amount']) 

			res.append({
				'post_name': post.name,
				'taxed': taxed or '-',
				'withheld': withheld or '-',
				'pending': pending or '-',
				'received': received or '-',				
			})

			self.totals.taxed += taxed
			self.totals.withheld += withheld
			self.totals.pending += pending
			self.totals.received += received
										
		return res
		
	def get_common_summary_projects(self,data):
		date_from = data['date_from']
		date_to = data['date_to']
		projects = self.get_projects(False)

		res = []

		for project in projects:
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 29 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			shortfall_data = self.cr.dictfetchall()[0]
			shortfall = int(0 if shortfall_data['amount'] is None else shortfall_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 30 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			tax_data = self.cr.dictfetchall()[0]
			tax = int(0 if tax_data['amount'] is None else tax_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 31 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			penalty_data = self.cr.dictfetchall()[0]
			penalty = int(0 if penalty_data['amount'] is None else penalty_data['amount'])

			self.cr.execute("select sum(credit) as amount from account.invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 35 \
				and aml.date >= %s and aml.date <= %s and ai.project_id = %s",(date_from,date_to,project.id))
			bankcharges_data = self.cr.dictfetchall()[0]
			bankcharges = int(0 if bankcharges_data['amount'] is None else bankcharges_data['amount']) 

			res.append({
				'project_name': project.name,
				'shortfall': shortfall or '-',
				'tax': tax or '-',
				'penalty': penalty or '-',
				'bankcharges': bankcharges or '-',				
			})

			self.totals.shortfall += shortfall
			self.totals.tax += tax
			self.totals.penalty += penalty
			self.totals.bankcharges += bankcharges
					
		return res
	
	def get_common_summary_centers(self,data):
		date_from = data['date_from']
		date_to = data['date_to']
		centers = self.get_centers(False)

		res = []

		for center in centers:
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 29 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			shortfall_data = self.cr.dictfetchall()[0]
			shortfall = int(0 if shortfall_data['amount'] is None else shortfall_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 30 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			tax_data = self.cr.dictfetchall()[0]
			tax = int(0 if tax_data['amount'] is None else tax_data['amount'])

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 31 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			penalty_data = self.cr.dictfetchall()[0]
			penalty = int(0 if penalty_data['amount'] is None else penalty_data['amount'])
			
			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 35 \
				and aml.date >= %s and aml.date <= %s and ai.center_id = %s",(date_from,date_to,center.id))
			bankcharges_data = self.cr.dictfetchall()[0]
			bankcharges = int(0 if bankcharges_data['amount'] is None else bankcharges_data['amount']) 

			res.append({
				'center_name': center.name,
				'shortfall': shortfall or '-',
				'tax': tax or '-',
				'penalty': penalty or '-',
				'bankcharges': bankcharges or '-',				
			})

			self.totals.shortfall += shortfall
			self.totals.tax += tax
			self.totals.penalty += penalty
			self.totals.bankcharges += bankcharges
						
		return res
		
	def get_shortfall_summary_posts(self,data,center_id,project_id):
		date_from = data['date_from']
		date_to = data['date_to']

		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)

		res = []

		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 29 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			shortfall_data = self.cr.dictfetchall()[0]
			shortfall = int(0 if shortfall_data['amount'] is None else shortfall_data['amount'])

			res.append({
				'post_name': post.name,
				'shortfall': shortfall or '-',				
			})

			self.totals.shortfall += shortfall
										
		return res
	
	def get_tax_summary_posts(self,data,center_id,project_id):
		date_from = data['date_from']
		date_to = data['date_to']

		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)

		res = []

		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 30 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			tax_data = self.cr.dictfetchall()[0]
			tax = int(0 if tax_data['amount'] is None else tax_data['amount'])

			res.append({
				'post_name': post.name,
				'tax': tax or '-',				
			})

			self.totals.tax += tax
											
		return res
	
	def get_penalty_summary_posts(self,data,center_id,project_id):
		date_from = data['date_from']
		date_to = data['date_to']

		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)

		res = []

		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 31 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			penalty_data = self.cr.dictfetchall()[0]
			penalty = int(0 if penalty_data['amount'] is None else penalty_data['amount'])

			res.append({
				'post_name': post.name,
				'penalty': penalty or '-',				
			})

			self.totals.penalty += penalty

		return res
	
	def get_bankcharges_summary_posts(self,data,center_id,project_id):
		date_from = data['date_from']
		date_to = data['date_to']
		
		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)

		res = []

		for post in posts:

			self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and aml.journal_id = 35 \
				and aml.date >= %s and aml.date <= %s and ai.post_id = %s",(date_from,date_to,post.id))
			bankcharges_data = self.cr.dictfetchall()[0]
			bankcharges = int(0 if bankcharges_data['amount'] is None else bankcharges_data['amount'])

			res.append({
				'post_name': post.name,
				'bankcharges': bankcharges or '-',				
			})

			self.totals.bankcharges += bankcharges
												
		return res
	
	
	def get_profitability_by_center(self,data,project_id=False):
		date_from = data['date_from']
		date_to = data['date_to']
		centers = self.get_centers(False)

		res = []

		for center in centers:
			if project_id:
				self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and \
					project_id = %s and journal_id = %s and state in ('open','paid')",(date_from,date_to,center.id,project_id,1))
			else:
				self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and \
					journal_id = %s and state in ('open','paid')",(date_from,date_to,center.id,1))
			invoiced_data = self.cr.dictfetchall()[0]	
			invoiced = int(invoiced_data['amount_untaxed'] or 0)
			
			if project_id:
				self.cr.execute("select sum(amount_total) as amount_total from account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and \
					project_id = %s and journal_id = %s and state in ('open','paid')",(date_from,date_to,center.id,project_id,3))
			else:
				self.cr.execute("select sum(amount_total) as amount_total from account_invoice where date_invoice >= %s and date_invoice <= %s and center_id = %s and \
					journal_id = %s and state in ('open','paid')",(date_from,date_to,center.id,3))
			credit_note_data = self.cr.dictfetchall()[0]
			credit_note = int(credit_note_data['amount_total'] or 0)
			
			if project_id:
				self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and \
					aml.date >= %s and aml.date <= %s and ai.center_id = %s and ai.project_id = %s and aml.journal_id = %s",(date_from,date_to,center.id,project_id,29))
			else:
				self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id and \
					aml.date >= %s and aml.date <= %s and ai.center_id = %s and aml.journal_id = %s",(date_from,date_to,center.id,29))
			shortfall_data = self.cr.dictfetchall()[0]
			shortfall = int(shortfall_data['amount'] or 0)
			
			net_invoiced = invoiced - shortfall

			if project_id:
				self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id \
					and gp.date_from >= %s and gp.date_to <= %s and gp.center_id = %s and gp.project_id = %s and code = %s and state in ('done')",(date_from,date_to,center.id,project_id,'BASIC'))
			else:
				self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id \
					and gp.date_from >= %s and gp.date_to <= %s and gp.center_id = %s and code = %s and state in ('done')",(date_from,date_to,center.id,'BASIC'))

			salary_data = self.cr.dictfetchall()[0]

			salary = int(salary_data['amount'] or 0)
			gross = net_invoiced - salary
			
			res.append({
				'name': center.name,
				'invoiced': invoiced,
				'shortfall': shortfall or '-',
				'net_invoiced': net_invoiced or '-',
				'salary': salary or '-',
				'gross': gross or '-',
			})
			
			self.totals.invoiced += invoiced
			self.totals.shortfall += shortfall
			self.totals.net_invoiced += net_invoiced
			self.totals.salary += salary
			self.totals.gross += gross
		return res
	
	def get_profitability_by_project(self,data,center_id=False):
		date_from = data['date_from']
		date_to = data['date_to']
		projects = self.get_projects(False)

		res = []

		for project in projects:
			if center_id:
				self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where project_id = %s and center_id = %s and journal_id = %s \
					and date_invoice >= %s and date_invoice <= %s and state in ('open','paid')",(project.id,center_id,1,date_from,date_to))
			else:
				self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where project_id = %s and journal_id = %s \
					and date_invoice >= %s and date_invoice <= %s and state in ('open','paid')",(project.id,1,date_from,date_to))
			invoiced_data = self.cr.dictfetchall()[0]	
			invoiced = int(invoiced_data['amount_untaxed'] or 0)

			if center_id:
				self.cr.execute("select sum(amount_total) as amount_total from account_invoice where project_id = %s and center_id = %s and journal_id = %s \
					and date_invoice >= %s and date_invoice <= %s and state in ('open','paid')",(project.id,center_id,3,date_from,date_to))
			else:			
				self.cr.execute("select sum(amount_total) as amount_total from account_invoice where project_id = %s and journal_id = %s \
					and date_invoice >= %s and date_invoice <= %s and state in ('open','paid')",(project.id,3,date_from,date_to))
			credit_note_data = self.cr.dictfetchall()[0]
			credit_note = int(credit_note_data['amount_total'] or 0)

			if center_id:
				self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id \
					and aml.date >= %s and aml.date <= %s and ai.project_id = %s and ai.center_id = %s and aml.journal_id = %s",(date_from,date_to,project.id,center_id,29))
			else:			
				self.cr.execute("select sum(credit) as amount from account_invoice ai, account_move_line aml where ai.id = aml.invoice_id \
					and aml.date >= %s and aml.date <= %s and ai.project_id = %s and aml.journal_id = %s",(date_from,date_to,project.id,29))
			shortfall_data = self.cr.dictfetchall()[0]
			shortfall = int(shortfall_data['amount'] or 0)

			net_invoiced = invoiced - shortfall

			if center_id:
				self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id \
					and gp.date_from >= %s and gp.date_to <= %s and gp.project_id = %s and center_id = %s and code = %s and state in ('done')",(date_from,date_to,project.id,center_id,'BASIC'))
			else:
				self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id \
					and gp.date_from >= %s and gp.date_to <= %s and gp.project_id = %s and code = %s and state in ('done')",(date_from,date_to,project.id,'BASIC'))

			salary_data = self.cr.dictfetchall()[0]

			salary = int(salary_data['amount'] or 0)
			gross = net_invoiced - salary
			
			res.append({
				'name': project.name,
				'invoiced': invoiced,
				'shortfall': shortfall or '-',
				'net_invoiced': net_invoiced or '-',
				'salary': salary or '-',
				'gross': gross or '-',
			})

			self.totals.invoiced += invoiced
			self.totals.shortfall += shortfall
			self.totals.net_invoiced += net_invoiced
			self.totals.salary += salary
			self.totals.gross += gross
		return res
		
	def get_invoices_comp_summary_posts(self,data,center_id,project_id):
		prid = data['period_id'][0]
		
		post_ids = self.pool.get('sos.post').search(self.cr,self.uid,[('center_id','=',center_id),('project_id','=',project_id)])
		posts = self.pool.get('sos.post').browse(self.cr,self.uid,post_ids)
		
		res = []

		for post in posts:
			
			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and post_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,post.id,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and post_id = %s and journal_id = %s and state in ('open','paid')",(prid-1,post.id, 3))
			credit_note = self.cr.dictfetchall()[0]
			prev_amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])


			self.cr.execute("select sum(amount_untaxed) as amount_untaxed from account_invoice where period_id = %s and post_id = %s and journal_id = %s and state in ('open','paid')",(prid,post.id,1))
			data = self.cr.dictfetchall()[0]	

			self.cr.execute("select sum(amount_total) as amount_total from account_invoice where period_id = %s and post_id = %s and journal_id = %s and state in ('open','paid')",(prid,post.id,3))
			credit_note = self.cr.dictfetchall()[0]

			amount = int(0 if data['amount_untaxed'] is None else data['amount_untaxed']) - int(0 if credit_note['amount_total'] is None else credit_note['amount_total'])
			diff = amount-prev_amount

			res.append({
				'post_name': post.name,
				'amount': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.prev_total += int(0 if prev_amount is None else prev_amount)
			self.totals.current_total += int(0 if amount is None else amount)
			self.totals.diff_total += int(0 if diff is None else diff)
								
		return res
		
	def get_payslips_summary(self,prid,prid2):
		period_obj = self.pool.get('sos.period')	
				
		self.totals = AttrDict({'diff':0})
		res = []
				
		self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and code = %s and state in ('done')",(prid-1,'BASIC'))
		data = self.cr.dictfetchall()[0]	

		prev_amount = data['amount'] 
		
		while prid <= prid2:  
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and code = %s and state in ('done')",(prid,'BASIC'))
			data = self.cr.dictfetchall()[0]	

			amount = data['amount'] 
			diff = int(0 if amount is None else amount) - int(0 if prev_amount is None else prev_amount)

			period = period_obj.browse(self.cr,self.uid,prid)

			res.append({
				'period_name': period.name,
				'amount': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.diff += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
				
		return res
	
	def get_payslips_summary_project(self,prid,prid2,project):
		period_obj = self.pool.get('sos.period')	
		
		self.totals = AttrDict({'diffprj':0})		
		res = []

		self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gpl.project_id = %s and code = %s and state in ('done')",(prid-1,project,'BASIC'))
		data = self.cr.dictfetchall()[0]
		
		prev_amount = data['amount'] 

		while prid <= prid2:  
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gpl.project_id = %s and code = %s and state in ('done')",(prid,project,'BASIC'))
			data = self.cr.dictfetchall()[0]	
						
			amount = data['amount'] 
			diff = int(0 if amount is None else amount) - int(0 if prev_amount is None else prev_amount)

			period = period_obj.browse(self.cr,self.uid,prid)

			res.append({
				'period_name': period.name,
				'amount_untaxed': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.diffprj += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
					
		return res
	
	def get_payslips_summary_center(self,prid,prid2,center_id):
		period_obj = self.pool.get('sos.period')	

		self.totals = AttrDict({'diffcnt':0})		
		res = []

		self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.center_id = %s and code = %s and state in ('done')",(prid-1,center_id,'BASIC'))
		data = self.cr.dictfetchall()[0]

		prev_amount = data['amount'] 

		while prid <= prid2:  
			self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gp.center_id = %s and code = %s and state in ('done')",(prid,center_id,'BASIC'))
			data = self.cr.dictfetchall()[0]	

			amount = data['amount'] 
			diff = int(0 if amount is None else amount) - int(0 if prev_amount is None else prev_amount)

			period = period_obj.browse(self.cr,self.uid,prid)

			res.append({
				'period_name': period.name,
				'amount_untaxed': amount,
				'amount_prev': prev_amount or '-',
				'diff': diff or '-',
			})

			self.totals.diffcnt += int(0 if diff is None else diff)
			prev_amount = amount
			prid = prid+1
						
		return res
	
	def get_guards_payslips_payable_project(self,project):
		
		self.cr.execute("select sum(gpl.total) as amount from guards_payslip gp, guards_payslip_line gpl where gp.id = gpl.slip_id and gp.period_id = %s and gpl.project_id = %s and code = %s and state in ('done')",(self.period_id,project,'BASIC'))
		data = self.cr.dictfetchall()[0]
			
		amount = data['amount'] 
		return amount
	
	def get_totals(self,code):		
		return self.totals[code]
		
	def get_byprj_total(self,fld):
		return self.total_byprj[fld]
