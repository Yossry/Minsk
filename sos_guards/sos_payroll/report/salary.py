
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp import pooler
import pdb
from operator import itemgetter
from itertools import groupby
from datetime import datetime

from common_reports import CommonReportHeaderWebkit
from webkit_parser_header_fix import HeaderFooterSOSWebKitParser

class SalaryWebkit(report_sxw.rml_parse, CommonReportHeaderWebkit):

	def __init__(self, cursor, uid, name, context):
		super(SalaryWebkit, self).__init__(cursor, uid, name, context=context)
		self.pool = pooler.get_pool(self.cr.dbname)
		self.cursor = self.cr
		
		company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
		#header_report_name = ' - '.join((_('Weapons'), company.name))
		header_report_name = '.'
		footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
		
		self.localcontext.update({
			'cr': cursor,
			'uid': uid,
			'report_name': _('Salary'),
			'filter_form': self._get_filter,
			'target_move': self._get_target_move,
			'guards': self._get_guards_br,
			'posts': self._get_posts_br,
			'additional_args': [
				('--header-font-name', 'Helvetica'),
				('--footer-font-name', 'Helvetica'),
				('--header-font-size', '10'),
				('--footer-font-size', '6'),				
				('--header-spacing', '2'),
				('--footer-left', footer_date_time),
				('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
				('--footer-line',),
			],
		})

	def set_context(self, objects, data, ids, report_type=None):
               
		# Reading form
		main_filter = self._get_form_param('filter', data, default='filter_no')
		group_by = self._get_form_param('group_by', data, default='guards')
		start_date = self._get_form_param('date_from', data)
		stop_date = self._get_form_param('date_to', data)
		do_centralize = self._get_form_param('centralize', data)
		
		# Retrieving Guards
		
		if group_by == 'guards':			
			new_ids = data['form']['guard_ids']
			guard_ids = new_ids		 
			
			if not guard_ids:
				post_ids = data['form']['post_ids']				
				guard_ids = self._get_posts_guards(post_ids, start_date, stop_date)
			
			if not guard_ids:
				center_ids = data['form']['center_ids']				
				guard_ids = self._get_centers_guards(center_ids, start_date, stop_date)
			
			if not guard_ids:
				project_ids = data['form']['project_ids']				
				guard_ids = self._get_projects_guards(project_ids, start_date, stop_date)
			
			salary_lines_memoizer = self._guard_salary_lines(guard_ids, main_filter, start_date, stop_date)
			objects = []
		
			for guard in self.pool.get('hr.employee').browse(self.cursor, self.uid, guard_ids):
				guard.salary_lines = salary_lines_memoizer.get(guard.id, [])
				objects.append(guard)
		
		elif  group_by == 'posts':
			new_ids = data['form']['post_ids']
			post_ids = new_ids
			
			if not post_ids:
				center_ids = data['form']['center_ids']				
				post_ids = self._get_centers_posts(center_ids)
			
			if not post_ids:
				project_ids = data['form']['project_ids']				
				post_ids = self._get_projects_posts(project_ids)
				
			salary_lines_memoizer = self._post_salary_lines(post_ids, main_filter, start_date, stop_date)
			objects = []
			
			for post in self.pool.get('sos.post').browse(self.cursor, self.uid, post_ids):
				post.salary_lines = salary_lines_memoizer.get(post.id, [])
				objects.append(post)
		
		self.localcontext.update({
			'start_date': start_date,
			'stop_date': stop_date,
			'group_by': group_by,
		})
		
		return super(SalaryWebkit, self).set_context(objects, data, new_ids, report_type=report_type)
		
	def _get_posts_guards(self, post_ids, date_start, date_stop):
		ids = []
		guard_post_obj = self.pool.get('sos.guard.post')
		search_period = [('post_id', 'in', post_ids),'|',('current','=',True),('fromdate', '>=', date_start),('fromdate', '<=', date_stop)]				
		search_ids = guard_post_obj.search(self.cursor, self.uid, search_period)
		guards = guard_post_obj.read(self.cursor, self.uid, search_ids,['guard_id'])
		for guard in guards:
			ids.append(guard['guard_id'][0])
		return ids	
	
	def _get_centers_guards(self, center_ids, date_start, date_stop):
		ids = []
		guards_obj = self.pool.get('hr.employee')
		search_period = [('center', 'in', center_ids),('current','=',True)]				
		guard_ids = guards_obj.search(self.cursor, self.uid, search_period)
		return guard_ids	
	
	def _get_projects_guards(self, project_ids, date_start, date_stop):
		ids = []
		guards_obj = self.pool.get('hr.employee')
		#search_period = [('project_id', 'in', project_ids),('current','=',True)]				
		search_period = [('project_id', 'in', project_ids)]				
		guard_ids = guards_obj.search(self.cursor, self.uid, search_period)
		return guard_ids	
	
	def _get_centers_posts(self, center_ids):
		ids = []
		posts_obj = self.pool.get('sos.post')
		#search_period = [('center_id', 'in', center_ids),('active','=',True)]				
		search_period = [('center_id', 'in', center_ids)]				
		post_ids = posts_obj.search(self.cursor, self.uid, search_period)
		
		search_period1 = [('center_id', 'in', center_ids),('active', '=', False)]				
		post_ids1 = posts_obj.search(self.cursor, self.uid, search_period1)
		for post in post_ids1:
			post_ids.append(post)
			
		return post_ids	
	
	def _get_projects_posts(self, project_ids):
		posts_obj = self.pool.get('sos.post')
				
		#search_period = [('project_id', 'in', project_ids),('active','=',True)]				
		search_period = [('project_id', 'in', project_ids)]				
		post_ids = posts_obj.search(self.cursor, self.uid, search_period)
		
		search_period1 = [('project_id', 'in', project_ids),('active', '=', False)]				
		post_ids1 = posts_obj.search(self.cursor, self.uid, search_period1)
		for post in post_ids1:
			post_ids.append(post)	
		
		return post_ids	
		
	def _get_guard_salary_ids_from_dates(self, guard_id, date_start, date_stop):
		salary_line_obj = self.pool.get('guards.payslip.line')
		#search_period = [('create_date', '>=', date_start),('create_date', '<=', date_stop),('employee_id', '=', guard_id),('code', '=', 'BASIC')]
		search_period = [('date_from', '>=', date_start),('date_to', '<=', date_stop),('employee_id', '=', guard_id),('code', '=', 'BASIC')]
				
		return salary_line_obj.search(self.cursor, self.uid, search_period)

	def _get_post_salary_ids_from_dates(self, post_id, date_start, date_stop):
		salary_line_obj = self.pool.get('guards.payslip.line')
		#search_period = [('create_date', '>=', date_start),('create_date', '<=', date_stop),('post_id', '=', post_id),('code', '=', 'BASIC')]
		search_period = [('date_from', '>=', date_start),('date_to', '<=', date_stop),('post_id', '=', post_id),('code', '=', 'BASIC')]
					
		return salary_line_obj.search(self.cursor, self.uid, search_period)
	
	def get_guard_salary_lines_ids(self, guard_id, main_filter, start_date, stop_date):
		if main_filter in ('filter_period', 'filter_no'):			
			return []
		elif main_filter == 'filter_date':
			return self._get_guard_salary_ids_from_dates(guard_id, start_date, stop_date)
		else:
			raise osv.except_osv(_('No valid filter'), _('Please set a valid time filter'))
	
	def get_post_salary_lines_ids(self, post_id, main_filter, start_date, stop_date):
		if main_filter in ('filter_period', 'filter_no'):			
			return []
		elif main_filter == 'filter_date':
			return self._get_post_salary_ids_from_dates(post_id, start_date, stop_date)
		else:
			raise osv.except_osv(_('No valid filter'), _('Please set a valid time filter'))
			
	def _get_salary_lines(self, salary_line_ids, ord_by):
		if not salary_line_ids:
			return []		
		
		if not isinstance(salary_line_ids, list):
			salary_line_ids = [salary_line_ids]
			
		monster ="""SELECT t.employee_id,t.post_id, emp.name_related,post.name, pl.number, pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,	t.rate,t.quantity, t.total,gc.name as contract_name
 			FROM guards_payslip_line t 
 			LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
 			LEFT JOIN sos_post post on (t.post_id=post.id)
 			LEFT JOIN guards_payslip pl on (t.slip_id=pl.id)
 			LEFT JOIN guards_contract gc on (pl.contract_id=gc.id)
 			WHERE t.id in %s"""
 			
		if ord_by == 'guard':
			monster += """ group by t.employee_id,t.post_id,name_related,post.name,pl.number, pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,t.quantity, t.total,gc.name"""
		else:
			monster += """ group by t.post_id,t.employee_id,name_related,post.name,pl.number, pl.paid, pl.bankacctitle,pl.bankacc,pl.accowner,t.rate,t.quantity, t.total,gc.name"""
			 				
		try:
			self.cursor.execute(monster, (tuple(salary_line_ids),))
			res= self.cursor.dictfetchall()
		except Exception:
			self.cursor.rollback()
			raise
		return res or []
	
	def _guard_salary_lines(self, guard_ids, main_filter,start_date, stop_date):
		res = {}
		for guard_id in guard_ids:
			salary_line_ids = self.get_guard_salary_lines_ids(guard_id, main_filter, start_date, stop_date)
			if not salary_line_ids:
				res[guard_id] = []
				continue
				
			lines = self._get_salary_lines(salary_line_ids, 'guard')
			res[guard_id] = lines
		return res	

	def _post_salary_lines(self, post_ids, main_filter,start_date, stop_date):
		res = {}
		for post_id in post_ids:
			salary_line_ids = self.get_post_salary_lines_ids(post_id, main_filter, start_date, stop_date)
			if not salary_line_ids:
				res[post_id] = []
				continue
				
			lines = self._get_salary_lines(salary_line_ids, 'post')
			res[post_id] = lines
		return res	

HeaderFooterSOSWebKitParser('report.sos_payroll.sos_report_salary_webkit', 'guards.payslip', 'addons/sos/report/templates/sos_report_salary.mako', parser=SalaryWebkit)
