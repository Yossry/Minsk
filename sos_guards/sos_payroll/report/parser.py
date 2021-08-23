
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
import pdb
from openerp import tools
from datetime import datetime, timedelta
from openerp.tools.amount_to_text_en import amount_to_text
import re


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
			'random':random,
			'hello_world':self.hello_world,	
			'amount_in_word': self.amount_in_word,
			'get_totals': self.get_totals,
			'get_head_salary': self.get_head_salary,
			'get_departments': self.get_departments,
			'get_regions': self.get_regions,
			'get_projects_from_slips': self.get_projects_from_slips,
			'get_projects_post': self.get_projects_post,
			'get_centers_post': self.get_centers_post,
			'get_projects_from_advices': self.get_projects_from_advices,
			'get_posts': self.get_posts,
			'_get_centers_posts': self._get_centers_posts,
			'_get_projects_posts': self._get_projects_posts,
			'post_salary_lines': self.post_salary_lines,
			'get_salary_lines': self.get_salary_lines,
			'_get_posts_guards': self._get_posts_guards,
			'_get_centers_guards': self._get_centers_guards,
			'_get_projects_guards': self._get_projects_guards,
			'get_guards': self.get_guards,
			'get_audit_salary_lines': self.get_audit_salary_lines,
			'get_invoice_days': self.get_invoice_days,
			'get_attendance_days': self.get_attendance_days,
			'guard_code_salary': self.guard_code_salary,
			'get_other_salary_lines': self.get_other_salary_lines,
			'remove_dashes' : self.remove_dashes,
		})
		self.totals = AttrDict({'post_total':0,'net_total':0,'post_days':0,'net_days':0,'wage':0,'basic':0,'fuel':0,'mobile':0,'allowence':0,'fine':0,'advance':0,'galaxy':0,'deduction':0,'net':0,'advised':0,'unadvised':0,'ud':0,
								'abl_incentive':0,'abl_net':0,'paid_leaves':0, 'total_present_days':0,'post_present_days':0,'post_paid_leaves':0,})
		self.date_start = '2015-01-01'
		self.date_stop = '2015-01-01'
		
	def hello_world(self, name):
		return "Hello, %s!" % name
		
	def amount_in_word(self, amount_total):
		return amount_to_text(amount_total,'en','PKR')
	
	def get_invoice_days(self, invoice_id):
		days = 0
		if invoice_id:
			sql="""select sum(quantity) days from account_invoice_line where invoice_id = %s"""
			self.cr.execute(sql%invoice_id)		
			days = self.cr.dictfetchone()['days'] or 0
		return days
		
	def guard_code_salary(self, guard_id, codes):
		sql="""select sum(t.total) amount from guards_payslip pl 
			left join guards_payslip_line t on (t.slip_id = pl.id) 
			where pl.employee_id = %s and pl.date_from >= %s and pl.date_to <= %s and code = %s"""
		self.cr.execute(sql,(guard_id,self.date_start,self.date_stop,codes))		
		amt = self.cr.dictfetchone()['amount'] or 0
		return amt
		
	def get_attendance_days(self, post_id,slip_number):
		sql="""select sum(quantity) days from guards_payslip pl 
			left join guards_payslip_line t on (t.slip_id = pl.id) 
			where pl.post_id = %s and code='BASIC' and pl.number = %s"""
		self.cr.execute(sql,(post_id,slip_number))		
		return self.cr.dictfetchone()['days'] or 0
	
	def get_audit_salary_lines(self, emp_id,data):
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']		
		
		sql ="""SELECT emp.id guardid, t.post_id, partner.name postname, pl.number slipnumber, pl.state slipstatus, t.rate guardrate,t.quantity dutydays, t.total salaryamt, gc.name as contract_name, inv.id invoiceid, inv.number invnumber, inv.state invstate
		 	FROM guards_payslip_line t 
		 	LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
		 	LEFT JOIN sos_post post on (t.post_id=post.id)
			LEFT JOIN res_partner partner on (post.partner_id = partner.id)
		 	LEFT JOIN guards_payslip pl on (t.slip_id=pl.id)
		 	LEFT JOIN guards_contract gc on (pl.contract_id=gc.id)
			LEFT JOIN account_invoice inv on (t.post_id = inv.post_id)
		 	WHERE emp.id = %s and pl.date_from >= %s and pl.date_to <= %s and tcode='BASIC' and inv.date_from >= %s and inv.date_to <= %s """		 			
		 	
		try:
			self.cr.execute(sql, (emp_id, start_date, stop_date, start_date, stop_date ))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise
		return res or []
		
	def get_salary_lines(self, salary_line_ids, ord_by):
		if not salary_line_ids:
			return []		
			
		if not isinstance(salary_line_ids, list):
			salary_line_ids = [salary_line_ids]
				
		monster ="""SELECT t.employee_id, emp.code, t.post_id, emp.name_related,partner.name, pl.number,t.slip_id, pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,
			t.rate,sum(t.quantity) as quantity, sum(t.total) as total,gc.name as contract_name, b.name as bank_name,pl.abl_incentive_amt as incentive,pl.paid_leaves,paid_leaves_post
	 		FROM guards_payslip_line t 
	 		LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
	 		LEFT JOIN sos_post post on (t.post_id=post.id)
			LEFT JOIN res_partner partner on (post.partner_id = partner.id)
	 		LEFT JOIN guards_payslip pl on (t.slip_id=pl.id)
	 		LEFT JOIN guards_contract gc on (pl.contract_id=gc.id)
	 		LEFT JOIN sos_bank b on (pl.bank=b.id)
	 		WHERE t.id in %s"""
	 			
	 	if ord_by == 'guard':
	 		monster += """ group by t.employee_id,emp.code,t.post_id,name_related,partner.name,pl.number,t.slip_id,pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,gc.name,b.name,pl.abl_incentive_amt,pl.paid_leaves,pl.paid_leaves_post  order by emp.name_related"""
	 	else:
	 		monster += """ group by t.post_id,t.employee_id,emp.code,name_related,partner.name,pl.number,t.slip_id,pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,gc.name,b.name,pl.abl_incentive_amt,pl.paid_leaves,pl.paid_leaves_post order by emp.name_related""" 				
	
		try:
			self.cr.execute(monster, (tuple(salary_line_ids),))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise
		return res or []
		
	def post_salary_lines(self, post_id, data):
		salary_line_obj = self.pool.get('guards.payslip.line')
		date_start = data['form']['date_from']
		date_stop = data['form']['date_to']
		display_incentive = data['form']['display_incentive']		
		
		self.totals.post_total = 0
		self.totals.post_days = 0
		self.totals.post_present_days = 0
		self.totals.post_paid_leaves = 0
		
		search_period = [('date_from', '>=', date_start),('date_to', '<=', date_stop),('post_id', '=', post_id),('code', '=', 'BASIC')]
		salary_line_ids = salary_line_obj.search(self.cr, self.uid, search_period, order='employee_id')
		if not salary_line_ids:
			return []
				
		lines = self.get_salary_lines(salary_line_ids, 'post')
		self.totals.abl_incentive = 0
		
		for line in lines:
			if line['paid_leaves_post'] and line['paid_leaves_post'] != post_id:
				line['paid_leaves'] = 0
			
			self.totals.post_total += line['total']
			self.totals.net_total += line['total']
			self.totals.post_days += line['quantity']
			self.totals.net_days += line['quantity']
			self.totals.abl_incentive += line['incentive']
			self.totals.paid_leaves +=line['paid_leaves'] or 0
			
			self.totals.post_paid_leaves +=line['paid_leaves'] or 0
			self.totals.post_present_days += (line['quantity'] - line['paid_leaves']) or 0
			self.totals.total_present_days += (line['quantity'] - line['paid_leaves']) or 0
			#self.totals.abl_net += line['incentive']
			
		## ABL NET Incentive Calc.
		if display_incentive:
			self.totals.abl_net = 0
			abl_incentive_ids = salary_line_obj.search(self.cr,self.uid,[('date_from', '>=', date_start),('code','=','ATTINC')])
			for abl_incentive_id in abl_incentive_ids:
				incentive_id = salary_line_obj.browse(self.cr,self.uid,abl_incentive_id)
				self.totals.abl_net += incentive_id.total 	
		return lines
		
	def get_other_salary_lines(self,slip_id,code=False):
		#pdb.set_trace()		
		payslip_line_obj = self.pool.get('guards.payslip.line')
		slip_id = slip_id
		code = code
		total = 0
		if slip_id and code =='NET':
			total = 0
			other_line_id= payslip_line_obj.search(self.cr,self.uid,[('slip_id', '=', slip_id),('code','=','NET')])
			other_line = payslip_line_obj.browse(self.cr,self.uid,other_line_id)
			total = other_line.total
		if slip_id and code =='Deduction':
			total = 0
			other_line_ids= payslip_line_obj.search(self.cr,self.uid,[('slip_id', '=', slip_id),('code','in',['UD','GSD','GLD','ADV'])])
			for other_line_id in other_line_ids:
				other_line = payslip_line_obj.browse(self.cr,self.uid,other_line_id)
				total += abs(other_line.total) or 0
		if slip_id and code =='Other':
			total = 0
			other_line_ids= payslip_line_obj.search(self.cr,self.uid,[('slip_id', '=', slip_id),('code','in',['ARRE','WP','DALW'])])
			for other_line_id in other_line_ids:
				other_line = payslip_line_obj.browse(self.cr,self.uid,other_line_id)
				total += other_line.total or 0				
		return total	
			
		
	def get_guards(self,data):
		guard_obj = self.pool.get('hr.employee')
		start_date = data['form']['date_from']
		stop_date = data['form']['date_to']			
		
		guard_ids = data['form']['guard_ids']
		
		if not guard_ids:
			post_ids = data['form']['post_ids']				
			if post_ids:
				guard_ids = self._get_posts_guards(post_ids, start_date, stop_date)
		
		if not guard_ids:
			center_ids = data['form']['center_ids']				
			if center_ids:
				guard_ids = self._get_centers_guards(center_ids, start_date, stop_date)
				
		if not guard_ids:
			project_ids = data['form']['project_ids']				
			if project_ids:
				guard_ids = self._get_projects_guards(project_ids, start_date, stop_date)
			
		guards = guard_ids and guard_obj.browse(self.cr,self.uid,guard_ids) or []	
		self.date_start = start_date
		self.date_stop = stop_date		
		return guards
		
	def _get_posts_guards(self, post_ids, start_date, stop_date):
		
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and name >= %s and name <= %s and att.post_id in %s order by to_number(code, '999999')"""
		
		try:
			self.cr.execute(sql, (start_date, stop_date, tuple(post_ids),))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise
		return  [x['employee_id'] for x in res] or []		
		
	def _get_centers_guards(self, center_ids, start_date, stop_date):
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and name >= %s and name <= %s and att.center_id in %s order by to_number(code, '999999')"""
				
		try:
			self.cr.execute(sql, (start_date, stop_date, tuple(center_ids),))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise
		return  [x['employee_id'] for x in res] or []		
	
	def _get_projects_guards(self, project_ids, start_date, stop_date):
		sql = """select distinct employee_id,to_number(code, '999999') from sos_guard_attendance att,hr_employee emp where att.employee_id = emp.id and name >= %s and name <= %s and att.project_id in %s order by to_number(code, '999999')"""
						
		try:
			self.cr.execute(sql, (start_date, stop_date, tuple(project_ids),))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise
	
		return  [x['employee_id'] for x in res] or []		
		
	def get_posts(self,data):
		p_obj = self.pool.get('sos.post')
		
		post_ids  = data['post_ids']
		
		if not post_ids:
			center_ids = data['center_ids'] and data['center_ids']
			if center_ids:
				post_ids = self._get_centers_posts(center_ids)

		if not post_ids:
			project_ids= data['project_ids'] and data['project_ids']
			if project_ids:
				post_ids = self._get_projects_posts(project_ids,data,False)	

		posts = p_obj.browse(self.cr,self.uid,post_ids)		
		return posts
		
	def _get_centers_posts(self, center_id):
		ids = []
		posts_obj = self.pool.get('sos.post')
		search_period = [('center_id', '=', center_id),('active','=',True)]				
		posts_id = posts_obj.search(self.cr, self.uid, search_period)
		return posts_id	
		
	def _get_projects_posts(self, project_ids,data,active=True):
		ids = []
		
		date_from = data['date_from']
		date_to = data['date_to']		

		posts_obj = self.pool.get('sos.post')

		dom = [('project_id', 'in', project_ids)]
		if active:
			dom += [('active','=',True)]
		
		post_ids = posts_obj.search(self.cr, self.uid, dom)
		
		if not active:
			dom = [('project_id', 'in', project_ids),('enddate','>=',date_from),('enddate','<=',date_to),('active','=',False)]
		post_ids2 = posts_obj.search(self.cr, self.uid, dom)		
		post_ids += post_ids2
	
		return post_ids	
		
	def get_head_salary(self,slip_id,code):
		payslip_line_obj = self.pool.get('hr.payslip.line')
		line_ids = payslip_line_obj.search(self.cr,self.uid,[('slip_id','=',slip_id),('code','=',code)])
		if line_ids:
			line = payslip_line_obj.browse(self.cr,self.uid,line_ids)[0]
			return line.total
		return 0
		
	def get_salary(self,payslip_ids):
		payslip_obj = self.pool.get('hr.payslip')
		lines = []			
		i = 1
		for payslip in payslip_obj.browse(self.cr,self.uid,payslip_ids):
			basic = self.get_head_salary(payslip.id,'BASIC')
			fuel = self.get_head_salary(payslip.id,'FALW')
			mobile = self.get_head_salary(payslip.id,'MALW')
			fine = self.get_head_salary(payslip.id,'FINE')
			advance = self.get_head_salary(payslip.id,'ADV')
			galaxy = self.get_head_salary(payslip.id,'GMD')
			net = self.get_head_salary(payslip.id,'NET')
			allowence = fuel+mobile
			deduction = fine+advance+galaxy
						
			d = AttrDict()
			d.name = payslip.employee_id.name_related
			d.designation = payslip.employee_id.job_id.name
			d.wage = payslip.contract_id.wage
			d.basic = basic
			d.fuel = fuel
			d.mobile = mobile
			d.allowence = allowence
			d.fine = fine
			d.advance = advance
			d.galaxy = galaxy
			d.deduction = deduction
			d.net = net
			d.counter = i
						
			self.totals.wage += d.wage
			self.totals.basic += d.basic
			self.totals.fuel += d.fuel
			self.totals.mobile += d.mobile
			self.totals.allowence += d.allowence
			self.totals.fine += d.fine
			self.totals.advance += d.advance
			self.totals.galaxy += d.galaxy
			self.totals.deduction += d.deduction
			self.totals.net += d.net

			i += 1
			lines.append(d)
		return lines
			
	def get_departments(self,start_date,end_date):
		dep_obj = self.pool.get('hr.department')		
		payslip_obj = self.pool.get('hr.payslip')
						
		ids = dep_obj.search(self.cr,self.uid,[])
		res = []
		for dept in dep_obj.browse(self.cr,self.uid,ids):
			payslip_ids = payslip_obj.search(self.cr,self.uid,[('date_from','>=',start_date),('date_to','<=',end_date),('employee_id.work_location','=','Head Office'),('employee_id.department_id','=',dept.id)])
			lines = self.get_salary(payslip_ids)
			res.append({
				'name': dept.name,
				'lines': lines,
			})		
		return res
	
	def get_regions(self,start_date,end_date):			
		payslip_obj = self.pool.get('hr.payslip')
				
		self.cr.execute("select distinct work_location from hr_employee where is_guard = False and work_location <> 'Head Office'")
		regions = self.cr.dictfetchall()
				
		res = []
		for region in regions:
			payslip_ids = payslip_obj.search(self.cr,self.uid,[('date_from','>=',start_date),('date_to','<=',end_date),('employee_id.work_location','=',region['work_location'])])
			lines = self.get_salary(payslip_ids)
			res.append({
				'name': region['work_location'],
				'lines': lines,
			})		
		return res
		
	def get_totals(self,code):		
		return self.totals[code]
		
	def get_projects_from_advices(self,invoice_id):			
		payslip_obj = self.pool.get('guards.payslip')
		project_obj = self.pool.get('sos.project')


		self.cr.execute("select distinct project_id from guards_payslip where advice_id = %s" %(invoice_id))
		projects = self.cr.dictfetchall()

		res = []

		for project in projects:
			project_id = project_obj.browse(self.cr,self.uid,[project['project_id']])[0]
			
			self.cr.execute("select sum(total) as total from guards_payslip where advice_id = %s" %(invoice_id))
			lines = self.cr.dictfetchall()
			advised = lines[0]['total']

			self.totals.advised += advised
			
			res.append({
				'name': project_id.name,
				'advised': advised,			
			})
		return res
	
	def get_projects_from_slips(self,start_date,end_date):			
		payslip_obj = self.pool.get('guards.payslip')
		project_obj = self.pool.get('sos.project')
		
	
		self.cr.execute("select distinct project_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		projects = self.cr.dictfetchall()

		res = []
				
		for project in projects:
			project_id = project_obj.browse(self.cr,self.uid,[project['project_id']])[0]
			
			self.cr.execute("select sum(total) as total from guards_payslip where advice_id is not NULL and project_id = %s and date_from >= %s and date_to <= %s",(project['project_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			advised = lines[0]['total']
			
			self.cr.execute("select sum(total) as total from guards_payslip where advice_id is NULL and project_id = %s and date_from >= %s and date_to <= %s",(project['project_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			unadvised = lines[0]['total']
			
			if advised:
				self.totals.advised += advised
			if unadvised:
				self.totals.unadvised += unadvised
			
			res.append({
				'name': project_id.name,
				'advised': advised,
				'unadvised': unadvised,
			})
		self.totals.net = self.totals.advised + self.totals.unadvised	
		return res
		
	def get_projects_post(self,start_date,end_date):			
		payslip_obj = self.pool.get('guards.payslip')
		project_obj = self.pool.get('sos.project')
		
	
		self.cr.execute("select distinct project_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		projects = self.cr.dictfetchall()

		res = []

		for project in projects:
			project_id = project_obj.browse(self.cr,self.uid,[project['project_id']])[0]
			
			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'BASIC' and l.project_id = %s and l.date_from >= %s and l.date_to <= %s",(project['project_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			advised = lines[0]['total'] or 0

			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is NULL and code = 'BASIC' and l.project_id = %s and l.date_from >= %s and l.date_to <= %s",(project['project_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			unadvised = lines[0]['total'] or 0
			
			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'UD' and l.project_id = %s and l.date_from >= %s and l.date_to <= %s",(project['project_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			ud = lines[0]['total'] or 0
			
			if advised:
				self.totals.advised += advised
			if unadvised:
				self.totals.unadvised += unadvised
			if ud:
				self.totals.ud += ud
				
			res.append({
				'name': project_id.name,
				'advised': advised,
				'ud': ud,
				'total': advised + unadvised,
				'unadvised': unadvised,
			})
		self.totals.net = self.totals.advised + self.totals.unadvised	
		return res
		
	def get_centers_post(self,start_date,end_date):			
		payslip_obj = self.pool.get('guards.payslip')
		center_obj = self.pool.get('sos.center')

		self.cr.execute("select distinct center_id from guards_payslip where date_from >= %s and date_to <= %s",(start_date,end_date))
		centers = self.cr.dictfetchall()

		res = []

		for center in centers:
			center_id = center_obj.browse(self.cr,self.uid,[center['center_id']])[0]

			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'BASIC' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			advised = lines[0]['total'] or 0

			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is NULL and code = 'BASIC' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			unadvised = lines[0]['total'] or 0

			self.cr.execute("select sum(l.total) as total from guards_payslip p, guards_payslip_line l where l.slip_id = p.id and advice_id is not NULL and code = 'UD' and p.center_id = %s and l.date_from >= %s and l.date_to <= %s",(center['center_id'],start_date,end_date))
			lines = self.cr.dictfetchall()
			ud = lines[0]['total'] or 0

			if advised:
				self.totals.advised += advised
			if unadvised:
				self.totals.unadvised += unadvised
			if ud:
				self.totals.ud += ud

			res.append({
				'name': center_id.name,
				'advised': advised,
				'ud': ud,
				'total': advised + unadvised,
				'unadvised': unadvised,
			})
		self.totals.net = self.totals.advised + self.totals.unadvised	
		return res
		
	def remove_dashes(self,name):
		return re.sub('-','',name)
	
		
