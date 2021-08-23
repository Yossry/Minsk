from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import random
import pdb
from openerp import tools
from datetime import datetime, timedelta
from pytz import timezone
from openerp.tools.amount_to_text_en import amount_to_text


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
			'get_totals': self.get_totals,
			'get_serial': self.get_serial,
			'get_date_formate' : self.get_date_formate,
			'get_date_time':self.get_date_time,
			'get_posts_guards':self.get_posts_guards,
			'_get_projects_posts':self._get_projects_posts,
			'_get_guards':self._get_guards,
			'_get_guard_att_ids_from_dates':self._get_guard_att_ids_from_dates,
			'_get_att_lines':self._get_att_lines,
			'_get_post_att_lines':self._get_post_att_lines,
			'_get_post_att_ids_from_dates':self._get_post_att_ids_from_dates,
			'get_posts':self.get_posts,
			'_get_centers_posts':self._get_centers_posts,
			'get_post_att_lines_ids':self.get_post_att_lines_ids,
			'_post_attendance_lines':self._post_attendance_lines,
			'_guard_attendance_lines':self._guard_attendance_lines,
			'get_centers': self.get_centers,
			'get_project_consolidated_attendance':self.get_project_consolidated_attendance,
			'get_project_coordinator':self.get_project_coordinator,
			'get_guards_project_absent':self.get_guards_project_absent,
			'get_guards_project_shortfall':self.get_guards_project_shortfall,
			'get_attendance_register_projects':self.get_attendance_register_projects,
			'_get_center_project_posts': self._get_center_project_posts,
			'get_attendance_register_post': self.get_attendance_register_post,
			'get_attendance_register_guard': self.get_attendance_register_guard,
			'get_center_guards': self.get_center_guards,
			
		})
		self.totals = AttrDict({'total':0,'serial':0,'total_present':0,'total_absent':0,'grand_total':0,'total_paid_leaves':0,'paid_leaves':0,})
		
	def get_serial(self):
		self.totals.serial = self.totals.serial + 1
		return self.totals.serial
		
	def get_date_formate(self,sdate):        
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')	
		
	def get_date_time(self):
		
		tz = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).partner_id.tz
		eastern = timezone(tz)
		loc_dt = datetime.now(eastern)
				
		fmt = '%A , %d.%m.%Y %H-%M %Z'
		return loc_dt.strftime(fmt)
	
	def _get_guards(self, data):
		employee_obj = self.pool.get('hr.employee')
		employee_ids = data['employee_ids']
		
		if not employee_ids:
			post_ids = data['post_ids']
			if post_ids:
				employee_ids = self.get_posts_guards(post_ids)
		if not employee_ids:
			center_ids = data['center_ids']
			if center_ids:
				employee_ids = self._get_centers_guards(center_ids)
		if not employee_ids:
			project_ids = data['project_ids']
			if project_ids:
				employee_ids = self._get_projects_guards(project_ids)

		employees =employee_obj.browse(self.cr,self.uid,employee_ids)
		return employees
		
	def get_posts(self, data):
		p_obj = self.pool.get('sos.post')
		post_ids  = data['post_ids']
		
		if not post_ids:
			center_ids = data['center_ids']
			if center_ids:
				post_ids = self._get_centers_posts(center_ids)
			
		if not post_ids:
			project_ids= data['project_ids']
			if project_ids:
				post_ids = self._get_projects_posts(project_ids)	
		
		posts = p_obj.browse(self.cr,self.uid,post_ids)		
		return posts
		
	def _post_attendance_lines(self, post_id,data):
		res = {}
		att_line_obj = self.pool.get('sos.guard.attendance')
		date_start  = data['date_from']
		date_stop  = data['date_to']
		post_id = post_id
		search_ids = [('name', '>=', date_start),('name', '<=', date_stop),('post_id', '=', post_id)]
		att_line_ids = att_line_obj.search(self.cr,self.uid,search_ids)
		if not att_line_ids:
			return []

		lines = self._get_att_lines(att_line_ids, 'post')
		return lines
	
		
	def get_post_att_lines_ids(self, post_id, start_date, stop_date):
	
		return self._get_post_att_ids_from_dates(post_id, start_date, stop_date)
	
	def _get_center_project_posts(self, project_id,center_id):
			
		posts_obj = self.pool.get('sos.post')
		domain = [('center_id', '=', center_id),('project_id', '=', project_id),('active','=',True)]				
		post_ids = posts_obj.search(self.cr, self.uid, domain)
		return posts_obj.browse(self.cr, self.uid, post_ids)	
	
	def get_center_guards(self, center_id):
				
		employee_obj = self.pool.get('hr.employee')
		domain = [('center_id', '=', center_id),('current','=',True)]				
		employee_ids = employee_obj.search(self.cr, self.uid, domain)
		return employee_obj.browse(self.cr, self.uid, employee_ids)	
		
	def _get_centers_posts(self, center_ids):
		ids = []
		posts_obj = self.pool.get('sos.post')
		domain = [('center_id', 'in', center_ids),('active','=',True)]				
		posts_id = posts_obj.search(self.cr, self.uid, domain)
		return posts_id	
		
	
	def _get_projects_posts(self, project_ids):
		ids = []
		posts_obj = self.pool.get('sos.post')
		domain = [('project_id', 'in', project_ids),('active','=',True)]				
		post_ids = posts_obj.search(self.cr, self.uid, domain)
		return post_ids		
	
	
	def get_posts_guards(self, post_ids):
		ids = []
		
		guard_posts_obj = self.pool.get('sos.guard.post')
		domain = [('post_id', 'in', post_id),('current','=',True)]
		search_ids = guard_posts_obj.search(self.cr, self.uid, domain)
		guards = guard_posts_obj.read(self.cr, self.uid, search_ids,['employee_id'])
		for guard in guards:
			ids.append(guard['employee_id'][0])
		return ids	
		
	def _get_centers_guards(self, center_ids):
		ids = []
		employee_obj = self.pool.get('hr.employee')
		domain = [('center', 'in', center_ids),('current','=',True)]				
		employee_ids = employee_obj.search(self.cr, self.uid, domain)
		return employee_ids
	
	def _get_projects_guards(self, project_ids):
		ids = []
		employee_obj = self.pool.get('hr.employee')
		domain = [('project_id', 'in', project_ids),('current','=',True)]				
		employee_ids = guards_obj.search(self.cr, self.uid, domain)
		return employee_ids
	
	def _get_post_att_ids_from_dates(self, post_id, date_start, date_stop):
		att_line_obj = self.pool.get('sos.guard.attendance')
		search_period = [('name', '>=', date_start),('name', '<=', date_stop),('post_id', '=', post_id)]

		return att_line_obj.search(self.cr, self.uid, search_period)

	
	def _get_att_lines(self, att_line_ids,ord_by):
		if not att_line_ids:
			return []		
		
		if not isinstance(att_line_ids, list):
			att_line_ids = [att_line_ids]
			
		monster ="""SELECT t.employee_id,t.post_id, emp.name_related,partner.name,emp.code,gc.name contract,guard.bankacctitle,guard.bankacc,bank.name bank1_name,
 			sum(CASE WHEN t.action = 'present' THEN 1 ELSE 0 END) AS present,
 			sum(CASE WHEN t.action = 'extra' THEN 1 ELSE 0 END) AS extra,
 			sum(CASE WHEN t.action = 'extra_double' THEN 1 ELSE 0 END) AS extra_double,
 			sum(CASE WHEN t.action = 'leave' THEN 1 ELSE 0 END) AS leave,
 			sum(CASE WHEN t.action = 'double' THEN 2 ELSE 0 END) AS double,
 			sum(CASE WHEN t.action = 'absent' THEN 1 ELSE 0 END) AS absent,
 			sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total
 			FROM sos_guard_attendance t 
 			LEFT JOIN hr_employee emp on (t.employee_id=emp.id)
			LEFT JOIN hr_guard guard on (emp.guard_id = guard.id)
 			LEFT JOIN sos_post post on (t.post_id=post.id)
			LEFT JOIN res_partner partner on (post.partner_id = partner.id)
 			LEFT JOIN guards_contract gc on (guard.guard_contract_id=gc.id)
 			LEFT JOIN sos_bank bank on (guard.bank_id=bank.id)
 			WHERE t.id in %s"""
 		if ord_by == 'guard':
 			monster += """ group by t.employee_id,t.post_id,emp.name_related,partner.name,emp.code,gc.name,guard.bankacctitle,guard.bankacc,bank.name"""
 		else:
 			monster += """ group by t.post_id,t.employee_id,emp.name_related,partner.name,emp.code,gc.name,guard.bankacctitle,guard.bankacc,bank.name"""		
		try:
			self.cr.execute(monster, (tuple(att_line_ids),))
			res= self.cr.dictfetchall()
		except Exception, exc:
			self.cr.rollback()
			raise		
		
		### Attendance Policy Code Here ###
		self.totals.paid_leaves = 0
		for r in res:
			paid_leaves = 0
			flag = True
						
			paid_ids = self.pool.get('guards.leave.policy').search(self.cr, self.uid, [('post_id','=',r['post_id'])], order="from_days desc")
			if not paid_ids:
				
				post_rec = self.pool.get('sos.post').browse(self.cr,self.uid,r['post_id'])
				center_id = self.pool.get('sos.center').search(self.cr,self.uid,[('id','=',post_rec.center_id.id)])
				project_id = self.pool.get('sos.project').search(self.cr,self.uid,[('id','=',post_rec.project_id.id)])
				
				paid_ids = self.pool.get('guards.leave.policy').search(self.cr, self.uid, [('center_id','=',center_id[0]),('project_id','=',project_id[0]),('post_id','=',False)], order="from_days desc")	
			paid_recs = self.pool.get('guards.leave.policy').browse(self.cr, self.uid,paid_ids)
			
			for paid_rec in paid_recs:
				if r['total'] >= paid_rec.from_days and flag:
					paid_leaves = paid_rec.leaves
					flag = False
			r['paid_leaves'] = paid_leaves
			r['total'] += paid_leaves
			self.totals.paid_leaves += paid_leaves
			self.totals.total_paid_leaves += paid_leaves				
				
		return res or []
		
		
		
	def _get_post_att_lines(self, att_line_ids):
		if not att_line_ids:
			return []		
		
		if not isinstance(att_line_ids, list):
			att_line_ids = [att_line_ids]
			
		monster ="""Select sum(CASE WHEN t.action = 'present' THEN 1 ELSE 0 END) AS present,
 			sum(CASE WHEN t.action = 'extra' THEN 1 ELSE 0 END) AS extra,
 			sum(CASE WHEN t.action = 'extra_double' THEN 1 ELSE 0 END) AS extra_double,
 			sum(CASE WHEN t.action = 'leave' THEN 1 ELSE 0 END) AS leave,
 			sum(CASE WHEN t.action = 'double' THEN 2 ELSE 0 END) AS double,
 			sum(CASE WHEN t.action = 'absent' THEN 1 ELSE 0 END) AS absent,
 			sum(CASE WHEN t.action = 'present' THEN 1 WHEN t.action = 'extra' THEN 1 WHEN t.action = 'double' THEN 2 WHEN t.action = 'extra_double' THEN 2  ELSE 0 END) AS total
 			FROM sos_guard_attendance t WHERE t.id in %s"""
 				
		try:
			self.cr.execute(monster, (tuple(att_line_ids),))
			res= self.cr.dictfetchall()
			
			### for Grand total Required by ayesha ###			
			self.totals.grand_total = self.totals.grand_total + res[0]['total']
			
		except Exception, exc:
			self.cr.rollback()
			raise
		return res or []
		
	def _guard_attendance_lines(self, employee_id, data):
		att_line_obj = self.pool.get('sos.guard.attendance')
		date_start  = data['date_from']
		date_stop  = data['date_to']
		domain = [('name', '>=', date_start),('name', '<=', date_stop),('employee_id', '=', employee_id)]
		
		att_line_ids = att_line_obj.search(self.cr,self.uid,domain)
		if not att_line_ids:
	 		return []
				
		lines = self._get_att_lines(att_line_ids, 'guard')
		return lines
		
		
	def get_guard_att_lines_ids(self, employee_id, start_date, stop_date):
		return self._get_post_att_ids_from_dates(employee_id, start_date, stop_date)
	
	def _get_guard_att_ids_from_dates(self, employee_id, date_start, date_stop):
		att_line_obj = self.pool.get('sos.guard.attendance')
		domain = [('name', '>=', date_start),('name', '<=', date_stop),('employee_id', '=', employee_id)]
		return att_line_obj.search(self.cr, self.uid, domain)
		
	def get_totals(self,code):		
		return self.totals[code]
		
		
	# Functions for the Daily Guard Attendance Report
	#
	
	def get_project_coordinator(self,project_id):
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[('id', '=', project_id)])
		project = project_obj.browse(self.cr,self.uid,project_ids)
		return project.project_coordinator_id.name_related
		
		
	
	def get_centers(self,data):
	
		project_id=data['form']['project_id'][0]
		date_to = data['form']['date_to']
		center_obj = self.pool.get('sos.center')
		
		res = []
		ids = center_obj.search(self.cr,self.uid,[])
		centers = center_obj.browse(self.cr,self.uid,ids)
		for center in centers:
			#self.cr.execute("select count(*) as total_guard from sos_post where project_id=%s and center_id=%s and active is True",(project_id,center.id))
			#total= self.cr.dictfetchall()[0]
			
			self.cr.execute("select count(*) as total_guard from hr_employee e, hr_guard g where e.guard_id = g.id and g.project_id=%s and g.center_id=%s and g.current is True and is_guard is True",(project_id,center.id))
			total= self.cr.dictfetchall()[0]
			
			self.cr.execute("select count(*) as present from sos_guard_attendance where project_id=%s and center_id=%s and action='present' and name=%s",(project_id,center.id,date_to))
			present_att= self.cr.dictfetchall()[0]
			
			self.cr.execute("select count(*) as absent from sos_guard_attendance where project_id=%s and center_id=%s and action='absent' and name=%s",(project_id,center.id,date_to))
			absent_att= self.cr.dictfetchall()[0]
			
			
			self.cr.execute("select h.name_related as name, h.code as ref from hr_employee h , sos_guard_attendance att, hr_guard g where h.id = att.employee_id and h.guard_id = g.id and att.project_id=%s and att.center_id=%s and att.name=%s and g.current is True and att.action='absent'",(project_id,center.id,date_to))
			absent_guard= self.cr.dictfetchall()
			
			res.append ({
				'name':center.code,
				'regional_head':center.regional_head_id.name_related,
				'supervisor':center.supervisor_id.name_related,
				'guard':total['total_guard'],
				'present':present_att['present'],
				'absent':absent_att['absent'],
				#'absent_name':absent_guard['name'],
				#'absent_id':absent_guard['ref'],
				'absent_guard':absent_guard,
				
				})
			self.totals.total = self.totals.total + total['total_guard']
			self.totals.total_present = self.totals.total_present + present_att['present']
			self.totals.total_absent = self.totals.total_absent + absent_att['absent']
		return res
		
	def get_project_consolidated_attendance(self,date_to):
		res = []
		
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])
		projects = project_obj.browse(self.cr,self.uid,project_ids)

		center_obj = self.pool.get('sos.center')
		center_ids = center_obj.search(self.cr,self.uid,[])
		centers = center_obj.browse(self.cr,self.uid,center_ids)
		
		for project in projects:
			total_guards = len(self.pool.get('hr.employee').search(self.cr, self.uid,[('project_id','=',project.id),('current','=',True),('is_guard','=',True)]))
			present_att = len(self.pool.get('sos.guard.attendance').search(self.cr, self.uid,[('project_id','=',project.id),('name','=',date_to),('action','in',['present','extra','double','extra_double'])]))
			absent_att = len(self.pool.get('sos.guard.attendance').search(self.cr, self.uid,[('project_id','=',project.id),('name','=',date_to),('action','=','absent')]))

			shortfall_list = []			
			center_count_list = []
			for center in centers:
				shortfall_count = len(self.pool.get('sos.guard.shortfall').search(self.cr, self.uid,[('project_id','=',project.id),('name','=',date_to),('center_id','=',center.id)]))
				if shortfall_count:				
					shortfall_list.append(center.code + " ("+ str(shortfall_count)+")")					
			
				center_count = 	len(self.pool.get('hr.employee').search(self.cr, self.uid,[('project_id','=',project.id),('center_id','=',center.id),('current','=',True),('is_guard','=',True)]))
				if center_count:				
					center_count_list.append(center.code +" ("+ str(center_count)+")")
	
			res.append ({
				'name':project.name,
				'coordinator':project.project_coordinator_id.name_related,
				'guard':total_guards,
				'present':present_att,
				'absent':absent_att,
				'shortfall': ', '.join(shortfall_list),
				'center_guards': ', '.join(center_count_list),
			})
			self.totals.total = self.totals.total + total_guards
			self.totals.total_present = self.totals.total_present + present_att
			self.totals.total_absent = self.totals.total_absent + absent_att	
		return res
		
	def get_guards_project_absent(self,data):
	
		#project_id=data['form']['project_id'][0]
		date_from =data['form']['date_from']
		date_to = data['form']['date_to']
		center_id = data['form']['center_id'][0]
		res = []
		
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])
		projects = project_obj.browse(self.cr,self.uid,project_ids)
		
		att_obj = self.pool.get('sos.guard.attendance')
		for project in projects:
		
			att_ids = att_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('project_id', '=',project.id),('name', '>=', date_from),('name', '<=', date_to ),('action', '=', 'absent')], order='name')
			att_rec = att_obj.browse(self.cr,self.uid,att_ids)
			for att in att_rec:
				res.append({
					'project_name':project.name,
					'guard':att.employee_id.name_related,
					'post':att.post_id.name,
					'date':att.name,
					})
		return res
		
	def get_guards_project_shortfall(self,data):
	
		#project_id=data['form']['project_id'][0]
		date_from = data['form']['date_from']
		date_to  =data['form']['date_to']
		center_id = data['form']['center_id'][0]
		
		res = []
		
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])
		projects = project_obj.browse(self.cr,self.uid,project_ids)
		
		shortfall_obj = self.pool.get('sos.guard.shortfall')
		for project in projects:
			shortfall_ids = shortfall_obj.search(self.cr,self.uid,[('project_id', '=', project.id),('center_id', '=', center_id),('name', '>=', date_from),('name', '<=', date_to)], order='project_id')
			sfs = shortfall_obj.browse(self.cr,self.uid,shortfall_ids)
			for sf in sfs:
				res.append({
					'project_name':project.name,
					'center_name':sf.center_id.code,
					'post_name':sf.post_id.name,
					'guard_name':sf.employee_id.name_related,
					'description':sf.description,
					'date': sf.name,
					'state':sf.state,
					})
		return res
		
	def get_attendance_register_projects(self,data):
		project_obj = self.pool.get('sos.project')
		center_id = data['form']['center_id'][0]
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		project_ids = []

		self.cr.execute("select distinct project_id from sos_guard_attendance where center_id=%s and name >= %s and name <=  %s",(center_id,date_from,date_to))
		projects = self.cr.dictfetchall()
		
		for x in projects:
			project_ids.append(x['project_id'])	
		
		return project_obj.browse(self.cr,self.uid,project_ids)
		
	def get_attendance_register_post(self,data,post_id):
		attendance_obj = self.pool.get('sos.guard.attendance')
		employee_obj = self.pool.get('hr.employee')
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		employee_ids = []
		guards = []

		self.cr.execute("select distinct employee_id from sos_guard_attendance where post_id=%s and name >= %s and name <=  %s",(post_id,date_from,date_to))
		guards_rec = self.cr.dictfetchall()
				
		for x in guards_rec:
			employee_ids.append(x['employee_id'])	
		
		sr = 1
		ptotal = 0
		for guard in employee_obj.browse(self.cr,self.uid,employee_ids):
			
			att_ids = attendance_obj.search(self.cr,self.uid,[('employee_id', '=', guard.id),('post_id', '=', post_id),('name', '>=', date_from),('name', '<=', date_to)], order='employee_id')
			atts = attendance_obj.browse(self.cr,self.uid,att_ids)
		
			gatt={'01':'','02':'','03':'','04':'','05':'','06':'','07':'','08':'','09':'','10':'','11':'','12':'','13':'','14':'','15':'','16':'','17':'','18':'','19':'','20':'','21':'','22':'','23':'','24':'','25':'','26':'','27':'','28':'','29':'','30':'','31':''}
			gatt['id']= guard.code	
			gatt['name']= guard.name_related	
			gatt['sr'] = sr
			sr += 1
			
			gtotal = 0			
			for att in atts:
				gatt[att.name[-2:]]= att.action[0].upper()
				if att.action[0].upper() == 'P':
					gtotal += 1
				elif att.action[0].upper() == 'E':
					gtotal += 1
				elif att.action[0].upper() == 'D':
					gtotal += 2
			gatt['total'] = gtotal
			guards.append(gatt)	
			
			ptotal += gtotal
		self.totals.total = ptotal
		return guards
		
	def get_attendance_register_guard(self,data,employee_id):
		attendance_obj = self.pool.get('sos.guard.attendance')
		post_obj = self.pool.get('sos.post')
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		post_ids = []
		posts = []

		self.cr.execute("select distinct post_id from sos_guard_attendance where employee_id=%s and name >= %s and name <=  %s",(employee_id,date_from,date_to))
		posts_rec = self.cr.dictfetchall()

		for x in posts_rec:
			post_ids.append(x['post_id'])	

		sr = 1
		gtotal = 0
		for post in post_obj.browse(self.cr,self.uid,post_ids):

			att_ids = attendance_obj.search(self.cr,self.uid,[('employee_id', '=', employee_id),('post_id', '=', post.id),('name', '>=', date_from),('name', '<=', date_to)], order='post_id')
			atts = attendance_obj.browse(self.cr,self.uid,att_ids)

			patt={'01':'','02':'','03':'','04':'','05':'','06':'','07':'','08':'','09':'','10':'','11':'','12':'','13':'','14':'','15':'','16':'','17':'','18':'','19':'','20':'','21':'','22':'','23':'','24':'','25':'','26':'','27':'','28':'','29':'','30':'','31':''}
			patt['id']=post.id	
			patt['name']=post.name
			patt['sr'] = sr
			sr += 1
			
			ptotal = 0
			for att in atts:
				patt[att.name[-2:]]=att.action[0].upper()
				if att.action[0].upper() == 'P':
					ptotal += 1
				elif att.action[0].upper() == 'E':
					ptotal += 1
				elif att.action[0].upper() == 'D':
					ptotal += 2
			patt['total'] = ptotal
			posts.append(patt)	

			gtotal += ptotal
		self.totals.total = gtotal
		return posts
			
		
