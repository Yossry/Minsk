

# from odoo.report import report_sxw
# from odoo.report.report_sxw import rml_parse
import random
import pdb
from odoo import tools
from datetime import datetime, timedelta
from pytz import timezone
# from odoo.tools.amount_to_text_en import amount_to_text
# from cStringIO import StringIO
# import qrcode

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
			'get_terminated_guards': self.get_terminated_guards,
			'get_joined_guards': self.get_joined_guards,
			'get_terminated_guards_summary': self.get_terminated_guards_summary,
			'get_terminated_posts_summary': self.get_terminated_posts_summary,
			'get_totals': self.get_totals,
			'get_joined_posts': self.get_joined_posts,
			'get_terminated_posts': self.get_terminated_posts,
			'get_guards_data_report':self.get_guards_data_report,
			'get_serial': self.get_serial,
			'get_date_formate': self.get_date_formate,
			'get_guards_missing_data_report':self.get_guards_missing_data_report,
			'get_guards_appointment_wise_report':self.get_guards_appointment_wise_report,
			'get_guards_create_date_wise_report':self.get_guards_create_date_wise_report,
			'get_guards_missing_data_project_wise':self.get_guards_missing_data_project_wise,
			'get_post_jobs':self.get_post_jobs,
			'get_center_projects':self.get_center_projects,
			'get_center_project_posts':self.get_center_project_posts,
			'get_project_centers':self.get_project_centers,
			'makeQRcode':self.makeQRcode,
			'get_guards_data_center_report':self.get_guards_data_center_report,
			'get_total_project_branches':self.get_total_project_branches,
			'get_total_project_guards':self.get_total_project_guards,
			'get_total_project_center_branches':self.get_total_project_center_branches,
			'get_total_project_center_guards':self.get_total_project_center_guards,
			'get_proeject_postwise_guards':self.get_proeject_postwise_guards,
			'get_center_postwise_guards':self.get_center_postwise_guards,
			'get_projects':self.get_projects,
			'get_centers':self.get_centers,
			'get_posts_report':self.get_posts_report,
			'get_date_formate1': self.get_date_formate1,
			
			
		})
		self.totals = AttrDict({'serial':0,'total_branches':0,'total_guards':0,'postwise_guards':0,'centerwise_guards':0,})
		
	def hello_world(self, name):
		return "Hello, %s!" % name
		
	def amount_in_word(self, amount_total):
		return amount_to_text(amount_total,'en','PKR')
		
	def get_serial(self):
		self.totals.serial = self.totals.serial+1
		return self.totals.serial
		
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d %H:%M:%S')
		return ss.strftime('%d %b %Y')
		
	def get_date_formate1(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')		
	
	def get_projects(self,project_ids=False):
		project_obj = self.pool.get('sos.project')

		if not project_ids:		
			project_ids = project_obj.search(self.cr,self.uid, [])

		projects = project_obj.browse(self.cr,self.uid,project_ids)
		return projects
	
	def get_centers(self,center_ids=False):
		center_obj = self.pool.get('sos.center')

		if not center_ids:
			center_ids = center_obj.search(self.cr,self.uid,[])

		centers = center_obj.browse(self.cr,self.uid,center_ids)
		return centers
		
	def get_center_project_posts(self, center_id, project_id):
		post_obj = self.pool.get('sos.post')
		post_ids = post_obj.search(self.cr, self.uid,[('center_id', '=', center_id),('project_id', '=', project_id),('active', '=', True)])
		posts = post_obj.browse(self.cr,self.uid,post_ids)	
	
		return posts
		
	def get_center_projects(self, center_id):
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])
		final_projects = []
		
		projects = project_obj.browse(self.cr,self.uid,project_ids)	
		for project in projects:
			post_ids = self.pool.get('sos.post').search(self.cr, self.uid,[('project_id', '=', project.id),('center_id', '=', center_id),('active', '=', True)])
			if post_ids:
				final_projects.append(project)
		return final_projects
		
	def get_project_centers(self, project_id):
		center_obj = self.pool.get('sos.center')
		center_ids = center_obj.search(self.cr,self.uid,[])
		final_centers = []

		centers = center_obj.browse(self.cr,self.uid,center_ids)	
		for center in centers:
			post_ids = self.pool.get('sos.post').search(self.cr, self.uid,[('project_id', '=', project_id),('center_id', '=', center.id),('active', '=', True)])
			if post_ids:
				final_centers.append(center)
		return final_centers
	
	def get_post_jobs(self, post_id):
		jobs_obj = self.pool.get('sos.post.jobs')
		jobs_ids = jobs_obj.search(self.cr, self.uid,[('post_id', '=', post_id)])
		jobs = jobs_obj.browse(self.cr,self.uid,jobs_ids)	
		
		res = []
		civil = ''
		armed = ''
		supervisor = ''
		for job in jobs:
			if job.contract_id.name == 'Civil':
				civil = ' ' + str(job.guards) + ' * ' + str(job.rate)
			if job.contract_id.name == 'Armed':
				armed = ' ' + str(job.guards) + ' * ' + str(job.rate)
			if job.contract_id.name == 'Supervisor':
				supervisor = ' ' + str(job.guards) + ' * ' + str(job.rate)
			
		res.append({
			'civil' : civil,
			'armed' : armed,
			'supervisor' : supervisor,
		})
		return res
		
	def makeQRcode(self, emp, size=2):
		
		code = 'Code:'+emp.code
		address = 'Address:'
		if emp.home_street:
			address = address + (emp.home_street or '')
		elif emp.street:
			address = address + (emp.street or '')
			
		mobile = 'Mobile:'+ (emp.mobile_phone or '')
		birthday = 'Birth:'+ (emp.birthday or '')
		account = 'Acc:'+ (emp.bankacc or '')
		bank = 'Bank:' + (emp.bank_id and emp.bank_id.name or '')
				
		lf ='\n'
		qr_string = lf.join([code,address,mobile,birthday,account,bank])
				
		qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=size)
		qr.add_data(qr_string)
		qr.make(fit=True)
		im = qr.make_image()
		tf = StringIO()
		im.save(tf, 'png')
		
		#pdb.set_trace()

		#size_x = str(im.size[0]/96.0)+'in'
		#size_y = str(im.size[1]/96.0)+'in'
		
		size_x = '0.88in'
		size_y = '0.88in'
		
		return tf, 'image/png', size_x, size_y
	
	def get_terminated_guards(self,date_from,date_to,order_by):			
		
		self.totals = AttrDict({'advised':0,'unadvised':0,'net':0})
		center_obj = self.pool.get('sos.center')
		center_ids = center_obj.search(self.cr,self.uid,[])
		
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])

		domain = [('project_id','in',project_ids),('center_id','in',center_ids),('todate','>=',date_from),('todate','<=',date_to),('to_reason','in',['terminate','escape'])]

		if order_by == 'post':
			order_by = 'post_id'
		elif order_by == 'center':
			order_by = 'center_id'
		elif order_by == 'appointmentdate':
			order_by = 'fromdate'			
		elif order_by == 'resigndate':
			order_by = 'todate'
		elif order_by == 'project':
			order_by = 'project_id'
		
		guard_post_ids = self.pool.get('sos.guard.post').search(self.cr,self.uid,domain,order=order_by)
		guard_posts = self.pool.get('sos.guard.post').browse(self.cr,self.uid,guard_post_ids)
		res = []

		i=1
		for guard_post in guard_posts:
			res.append({
				'sr': i,
				'name': guard_post.employee_id.name_related,
				'id': guard_post.employee_id.code,
				'post': guard_post.post_id.name,
				'center': guard_post.center_id.name,
				'project' : guard_post.project_id.name,
				'mobile' : guard_post.employee_id.mobile_phone,
				'cnic' : guard_post.employee_id.cnic,
				'appointmentdate' : guard_post.employee_id.appointmentdate,
				'resigdate' : guard_post.employee_id.resigdate,
				'to_date' : guard_post.todate,
			})
			i += 1
		return res
		
	def get_joined_guards(self,date_from,date_to,order_by):			
		center_obj = self.pool.get('sos.center')
		center_ids = center_obj.search(self.cr,self.uid,[])
		
		project_obj = self.pool.get('sos.project')
		project_ids = project_obj.search(self.cr,self.uid,[])

		domain = [('project_id','in',project_ids),('center_id','in',center_ids),('appointmentdate','>=',date_from),('appointmentdate','<=',date_to)]
		if order_by == 'post':
			order_by = 'current_post_id'	

		elif order_by == 'center':
			order_by = 'center_id'			
			
		elif order_by == 'appointmentdate':
			order_by = 'appointmentdate'			

		elif order_by == 'resigndate':
			order_by = 'resigndate'			

		elif order_by == 'project':
			order_by = 'project_id'			
			
		guard_ids = self.pool.get('hr.employee').search(self.cr,self.uid,domain,order=order_by)
		guards = self.pool.get('hr.employee').browse(self.cr,self.uid,guard_ids)
		res = []

		i=1
		for guard in guards:
			res.append({
				'sr': i,
				'name': guard.name_related,
				'id': guard.code,
				'post': guard.current_post_id.name,
				'center': guard.center_id.name,
				'project' : guard.project_id.name,
				'mobile' : guard.mobile_phone,
				'cnic' : guard.cnic,
				'appointmentdate' : guard.appointmentdate,
				'resigdate' : guard.resigdate,
				'to_date' : '',
			})
			i += 1
		return res
		
	def get_terminated_guards_summary(self,date_from,date_to,group_by):			
			
		self.totals = AttrDict({'current':0,'unknown':0,'escaped':0,'joined':0,'terminated':0,'transfered':0,'joined_guards':0,'terminated_guards':0})
		i=1
		res = []

		if group_by == 'center':
			center_obj = self.pool.get('sos.center')
			center_ids = center_obj.search(self.cr,self.uid,[])
		
			project_obj = self.pool.get('sos.project')
			project_ids = project_obj.search(self.cr,self.uid,[])

			centers = center_obj.browse(self.cr,self.uid,center_ids)	
			for center in centers:
				employee_ids = self.pool.get('hr.employee').search(self.cr, self.uid,[('center_id', '=', center.id),('project_id', 'in', project_ids),('current', '=', True)])
				emp_count = len(employee_ids)
				
				self.cr.execute("select SUM(CASE WHEN to_reason is Null THEN 1 ELSE 0 END) AS unknown, \
						SUM(CASE WHEN to_reason = 'transfer' THEN 1 ELSE 0 END) AS transfer, \
						SUM(CASE WHEN to_reason = 'terminate' THEN 1 ELSE 0 END) AS terminate, \
						SUM(CASE WHEN to_reason = 'escape' THEN 1 ELSE 0 END) AS escape \
						from sos_guard_post j, sos_post p where j.post_id = p.id \
						and p.center_id = %s and j.todate >= %s and j.todate <= %s and j.project_id in %s",(center.id,date_from,date_to,tuple(project_ids)))
				center_shifting = self.cr.dictfetchall()[0]

				self.cr.execute("select count(*) as joined from hr_employee e, hr_guard g where e.guard_id = g.id and center_id = %s and \
					appointmentdate >= %s and appointmentdate <= %s and project_id in %s",(center.id,date_from,date_to,tuple(project_ids)))
				center_joining = self.cr.dictfetchall()[0]
				res.append({
					'sr': i,
					'name': center.name,
					'current': emp_count,
					'terminated': center_shifting['terminate'] or '-',
					'transfered': center_shifting['transfer'] or '-',
					'escaped': center_shifting['escape'] or '-',
					'joined': center_joining['joined'] or '-',
					'unknown': center_shifting['unknown'] or '-',
				})
				self.totals.current += emp_count
				i = i+1

				self.totals.terminated += center_shifting['terminate'] or 0
				self.totals.escaped += center_shifting['escape'] or 0
				self.totals.transfered += center_shifting['transfer'] or 0
				self.totals.unknown += center_shifting['unknown'] or 0
				self.totals.joined += center_joining['joined'] or 0
						
		elif group_by == 'project':
			project_obj = self.pool.get('sos.project')
			project_ids = project_obj.search(self.cr,self.uid,[])

			center_obj = self.pool.get('sos.center')
			center_ids = center_obj.search(self.cr,self.uid,[])
		
			projects = project_obj.browse(self.cr,self.uid,project_ids)	
			for project in projects:
				employee_ids = self.pool.get('hr.employee').search(self.cr, self.uid,[('project_id', '=', project.id),('center_id', 'in', center_ids),('current', '=', True)])
				emp_count = len(employee_ids)

				self.cr.execute("select SUM(CASE WHEN to_reason is Null THEN 1 ELSE 0 END) AS unknown, \
						SUM(CASE WHEN to_reason = 'transfer' THEN 1 ELSE 0 END) AS transfer, \
						SUM(CASE WHEN to_reason = 'terminate' THEN 1 ELSE 0 END) AS terminate, \
						SUM(CASE WHEN to_reason = 'escape' THEN 1 ELSE 0 END) AS escape \
						from sos_guard_post j, sos_post p where j.post_id = p.id and \
						j.project_id = %s and j.todate >= %s and j.todate <= %s and p.center_id in %s",(project.id,date_from,date_to,tuple(center_ids)))
				project_shifting = self.cr.dictfetchall()[0]

				self.cr.execute("select count(*) as joined from hr_employee e, hr_guard g where e.guard_id=g.id and project_id = %s and \
					appointmentdate >= %s and appointmentdate <= %s and center_id in %s",(project.id,date_from,date_to,tuple(center_ids)))
				project_joining = self.cr.dictfetchall()[0]
				res.append({
					'sr': i,
					'name': project.name,
					'current': emp_count,
					'terminated': project_shifting['terminate'] or '-',
					'transfered': project_shifting['transfer'] or '-',
					'escaped': project_shifting['escape'] or '-',
					'joined': project_joining['joined'] or '-',
					'unknown': project_shifting['unknown'] or '-',
				})
				self.totals.current += emp_count
				i = i+1
				
				self.totals.terminated += project_shifting['terminate'] or 0
				self.totals.escaped += project_shifting['escape'] or 0
				self.totals.transfered += project_shifting['transfer'] or 0
				self.totals.unknown += project_shifting['unknown'] or 0
				self.totals.joined += project_joining['joined'] or 0
					
		return res
	
	def get_joined_posts(self,data,order_by):			

		self.totals = AttrDict({'joined_guards':0})
		center_ids = tuple(data['center_ids']) or tuple(self.pool.get('sos.center').search(self.cr, self.uid,[]))

		if order_by == 'center':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s order by centername",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'startdate':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by startdate",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'post':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by postname",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'enddate':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by enddate",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'project':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by project_id",(data['date_from'],data['date_to'],center_ids))

		posts = self.cr.dictfetchall()

		res = []

		i=1
		for post in posts:
			res.append({
				'sr': i,
				'name': post['postname'],
				'id': post['id'],				
				'center': post['centername'],
				'startdate' : post['startdate'],
				'enddate' : post['enddate'],
				'guards': post['guards'],
			})
			self.totals.joined_guards += post['guards']
			i += 1
		return res
	
	def get_terminated_posts(self,data,order_by):			
				
		self.totals = AttrDict({'terminated_guards':0})
		center_ids = tuple(data['center_ids']) or tuple(self.pool.get('sos.center').search(self.cr, self.uid,[]))

		if order_by == 'center':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by centername",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'startdate':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by startdate",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'post':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by postname",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'enddate':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by enddate",(data['date_from'],data['date_to'],center_ids))
		elif order_by == 'project':
			self.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by project_id",(data['date_from'],data['date_to'],center_ids))

		posts = self.cr.dictfetchall()

		res = []

		i=1
		for post in posts:
			res.append({
				'sr': i,
				'name': post['postname'],
				'id': post['id'],				
				'center': post['centername'],
				'startdate' : post['startdate'],
				'enddate' : post['enddate'],
				'guards': post['guards'],
			})
			self.totals.terminated_guards += post['guards']
			i += 1
		return res
		
	def get_terminated_posts_summary(self,data,group_by):			
		self.totals = AttrDict({'joined':0,'terminated':0})
		center_ids = tuple(data['center_ids']) or tuple(self.pool.get('sos.center').search(self.cr, self.uid,[]))
		if group_by == 'center':
			self.cr.execute("select c.name centername,count(*) as cnt from sos_post p, sos_center c where p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s group by centername",(data['date_from'],data['date_to'],center_ids))
		elif group_by == 'project':
			self.cr.execute("select c.name centername,count(*) as cnt from sos_post p, sos_project c where p.project_id = c.id and enddate >= %s and enddate <= %s and center_id in %s group by centername",(data['date_from'],data['date_to'],center_ids))

		posts = self.cr.dictfetchall()

		res = []

		i=1
		for post in posts:
			res.append({
				'sr': i,
				'name': post['centername'],				
				'terminated' : post['cnt'],
				'joined' : '-',
			})
			i += 1
			self.totals.terminated += post['cnt']

		if group_by == 'center':
			self.cr.execute("select c.name centername,count(*) as cnt from sos_post p, sos_center c where p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s group by centername",(data['date_from'],data['date_to'],center_ids))
		elif group_by == 'project':
			self.cr.execute("select c.name centername,count(*) as cnt from sos_post p, sos_project c where p.project_id = c.id and startdate >= %s and startdate <= %s and center_id in %s group by centername",(data['date_from'],data['date_to'],center_ids))

		posts = self.cr.dictfetchall()

		for post in posts:
			r = next((item['sr'] for item in res if item["name"] == post['centername']), None)
			if r:
				res[r-1]['joined'] = post['cnt']
			else:
				res.append({
					'sr': i,
					'name': post['centername'],				
					'joined' : post['cnt'],
					'terminated' : '-',
				})
				i += 1
			self.totals.joined += post['cnt']
			
		return res
	
	def get_guards_data_report(self,project_id):
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('project_id', '=', project_id),('current','=',True)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards
		
	def get_guards_data_center_report(self,center_id):
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('center_id', '=', center_id),('current','=',True)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards	
	
	def get_guards_missing_data_report(self,center_id):
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('center_id', '=', center_id),('current','=',True)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards
		
		
	def get_guards_missing_data_project_wise(self,project_id):
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('project_id', '=', project_id),('current','=',True)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards	
		
		
	def get_guards_appointment_wise_report(self,data):
	
		center = data['form']['center'][0]
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('center_id', '=', center),('current','=',True),('appointmentdate', '>=', date_from),('appointmentdate', '<=', date_to)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards
		
		
	def get_guards_create_date_wise_report(self,data):
	
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		
		
		guards_obj = self.pool.get('hr.employee')
		guards_ids = guards_obj.search(self.cr, self.uid,[('current','=',True),('create_date', '>=', date_from),('create_date', '<=', date_to)],order='current_post_id')
		guards = guards_obj.browse(self.cr,self.uid,guards_ids)
		return guards
		
		
	def get_total_project_center_branches(self,center_id, project_id):
		self.cr.execute("select count(*) from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s and project_id = %s",(center_id,project_id))
		posts = self.cr.dictfetchall()[0]
		#self.totals.total_branches += posts['count']		
		return posts['count']
		
	def get_total_project_center_guards(self, center_id,project_id):
		res = []
		self.cr.execute("select sum(guards) qty from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and center_id = %s and project_id = %s",(center_id,project_id))
		guards = self.cr.dictfetchall()[0]	
		#self.totals.total_guards += guards['qty']		
		return guards['qty']
	
	def get_total_project_branches(self,project_id):
		self.cr.execute("select count(*) from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and project_id = %s"%project_id)
		posts = self.cr.dictfetchall()[0]
		self.totals.total_branches += posts['count']		
		return posts['count']
		
	def get_total_project_guards(self, project_id):
		res = []
		self.cr.execute("select sum(guards) qty from sos_post pp, res_partner p where pp.id = p.post_id and p.active = True and project_id = %s"%project_id)
		guards = self.cr.dictfetchall()[0]	
		self.totals.total_guards += guards['qty']		
		return guards['qty']	
		
	def get_proeject_postwise_guards(self,center_id, project_id):
		post_obj = self.pool.get('sos.post')
		post_ids = post_obj.search(self.cr,self.uid,[('center_id', '=', center_id),('project_id', '=', project_id), ('active', '=', True)], order='name')
		posts = post_obj.browse(self.cr,self.uid,post_ids)
		res = []
		for post in posts:
		
			self.cr.execute("select guards as qty from sos_post pp, res_partner p where p.post_id = pp.id and active = True and pp.id= %s"%post.id)
			guards = self.cr.dictfetchall()[0]
			
			res.append ({
				'name' : post.name,
				'total' :guards['qty']
				
			})
			
			self.totals.postwise_guards += guards['qty']
		return res
		
	def get_center_postwise_guards(self, center_id,project_id):
		post_obj = self.pool.get('sos.post')
		post_ids = post_obj.search(self.cr,self.uid,[('center_id', '=', center_id), ('project_id', '=', project_id),('active', '=', True)],order='name')
		posts = post_obj.browse(self.cr,self.uid,post_ids)
		res = []
		
		for post in posts:
		
			self.cr.execute("select guards as qty from sos_post pp, res_partner p where p.post_id = pp.id and active = True  and pp.id = %s"%post.id)
			guards = self.cr.dictfetchall()[0]
			
			res.append ({
				'name' : post.name,
				'total' :guards['qty']
				
			})
			
			self.totals.centerwise_guards += guards['qty']
		return res	
	
	def get_posts_report(self,data):
			
		center_id = data['form']['center_id'][0]
		city_id = data['form']['city_id'][0]
		post_obj = self.pool.get('sos.post')
		post_ids = post_obj.search(self.cr, self.uid,[('active','=',True),('center_id', '=', center_id),('postcity', '=', city_id)],order='name')
		posts = post_obj.browse(self.cr,self.uid,post_ids)
		return posts	
	
	def get_totals(self,code):		
		return self.totals[code]
