import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class PostsJoinTerminationReport(models.AbstractModel):
	_name = 'report.sos.report_posts_jointermination'
	_description = 'SOS Posts Join Termination Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	##
	def get_terminated_posts_summary(self,data,group_by):			
		terminated = 0
		joined = 0
		res = []
		
		center_ids = data['center_ids']
		if not center_ids:
			center_ids = self.env['sos.center'].search([])
			center_ids = center_ids.ids
		
		if group_by == 'center':
			self.env.cr.execute("select c.name centername,c.id as center_id,count(*) as cnt from sos_post p, sos_center c where p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s group by centername,c.id",(data['date_from'],data['date_to'],tuple(center_ids)))
			posts = self.env.cr.dictfetchall()
			for p in posts:
				self.env.cr.execute("select sum(p.guards) as guards from  sos_post p,  sos_center c, res_partner res where p.center_id = c.id and p.partner_id = res.id and res.active is True and c.id= %s" %(p['center_id']))
				guards = self.env.cr.dictfetchall()
				p['total']=guards[0]['guards']
		

		elif group_by == 'project':
			self.env.cr.execute("select c.name centername,c.id as center_id, count(*) as cnt from sos_post p, sos_project c where p.project_id = c.id and enddate >= %s and enddate <= %s and center_id in %s group by centername,c.id",(data['date_from'],data['date_to'],tuple(center_ids)))
			posts = self.env.cr.dictfetchall()

			for p in posts:
					self.env.cr.execute("select sum(p.guards) as guards from  sos_post p,  sos_project c, res_partner res where p.project_id = c.id and p.partner_id = res.id and res.active is True and c.id= %s" %(p['center_id']))
					guards = self.env.cr.dictfetchall()
					p['total']= guards[0]['guards']

		i=1
		for post in posts:
			res.append({
				'sr': i,
				'name': post['centername'],	
				'total' : post['total'],			
				'terminated' : post['cnt'],
				'joined' : '-',
			})
			i += 1
			terminated += post['cnt']
		
		if group_by == 'center':
			self.env.cr.execute("select c.name centername,c.id as center_id,count(*) as cnt from sos_post p, sos_center c where p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s group by centername, c.id",(data['date_from'],data['date_to'],tuple(center_ids)))
			posts = self.env.cr.dictfetchall()
			# this code is missing
			for p in posts:
				self.env.cr.execute("select sum(p.guards) as guards from  sos_post p,  sos_center c, res_partner res where p.center_id = c.id and p.partner_id = res.id and res.active is True and c.id= %s" %(p['center_id']))
				guards = self.env.cr.dictfetchall()
				p['total']=guards[0]['guards']
		

		elif group_by == 'project':
			self.env.cr.execute("select c.name centername,c.id as project_id, count(*) as cnt from sos_post p, sos_project c where p.project_id = c.id and startdate >= %s and startdate <= %s and center_id in %s group by centername,c.id",(data['date_from'],data['date_to'],tuple(center_ids)))
			posts = self.env.cr.dictfetchall()
			for p in posts:
				self.env.cr.execute("select sum(p.guards) as guards from  sos_post p,  sos_project c, res_partner res where p.project_id = c.id and p.partner_id = res.id and res.active is True and c.id= %s" %(p['project_id']))
				guards = self.env.cr.dictfetchall()
				p['total']=guards[0]['guards']
				

		for post in posts:
			r = next((item['sr'] for item in res if item["name"] == post['centername']), None)
			if r:
				res[r-1]['joined'] = post['cnt']
			else:
				res.append({
					'sr': i,
					'name': post['centername'],
					'total' : post['total'],				
					'joined' : post['cnt'],
					'terminated' : '-',
				})
				i += 1
			joined += post['cnt']
		return res,terminated,joined
		
	##
	def get_joined_posts(self,data,order_by):			
		
		joined_guards = 0
		res = []
		
		center_ids = data['center_ids']
		if not center_ids:
			center_ids = self.env['sos.center'].search([])
			center_ids = center_ids.ids
		
		if order_by == 'center':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s order by centername",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'startdate':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by startdate",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'post':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by postname",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'enddate':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by enddate",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'project':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and startdate >= %s and startdate <= %s and center_id in %s  order by project_id",(data['date_from'],data['date_to'],tuple(center_ids)))

		posts = self.env.cr.dictfetchall()
		for post in posts:
			res.append({
				'name': post['postname'],
				'id': post['id'],				
				'center': post['centername'],
				'startdate' : post['startdate'],
				'enddate' : post['enddate'],
				'guards': post['guards'],
			})
			joined_guards += post['guards']
		return res,joined_guards
		
	##	
	def get_terminated_posts(self,data,order_by):			
				
		terminated_guards = 0
		res = []
		
		
		center_ids = data['center_ids']
		if not center_ids:
			center_ids = self.env['sos.center'].search([])
			center_ids = center_ids.ids

		if order_by == 'center':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by centername",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'startdate':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by startdate",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'post':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by postname",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'enddate':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by enddate",(data['date_from'],data['date_to'],tuple(center_ids)))
		elif order_by == 'project':
			self.env.cr.execute("select p.id,pp.name postname,c.name centername,p.project_id,startdate,enddate,guards from sos_post p, res_partner pp, sos_center c where p.partner_id = pp.id and p.center_id = c.id and enddate >= %s and enddate <= %s and center_id in %s  order by project_id",(data['date_from'],data['date_to'],tuple(center_ids)))

		posts = self.env.cr.dictfetchall()
		for post in posts:
			res.append({
				'name': post['postname'],
				'id': post['id'],				
				'center': post['centername'],
				'startdate' : post['startdate'],
				'enddate' : post['enddate'],
				'guards': post['guards'],
			})
			terminated_guards += post['guards']
		return res,terminated_guards			
		
	
	@api.model
	def _get_report_values(self, docids, data=None):
		center_recs,center_terminated,center_joined = self.get_terminated_posts_summary(data['form'],'center')
		project_recs,project_terminated,project_joined = self.get_terminated_posts_summary(data['form'],'project')
		
		joined_posts,joined_total = self.get_joined_posts(data['form'],data['form']['order_by'])
		terminated_posts,terminated_total = self.get_terminated_posts(data['form'],data['form']['order_by'])
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_posts_jointermination')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Center_Recs' : center_recs or False,
			'Center_Terminated' : center_terminated or 0,
			'Center_Jointed' : center_joined or 0,
			
			'Project_Recs' : project_recs or False,
			'Project_Terminated' : project_terminated or 0,
			'Project_Jointed' : project_joined or 0,
			
			'Joined_Posts' : joined_posts or False,
			'Joined_Total' : joined_total or 0,
			'Terminated_Posts' : terminated_posts or False,
			'Terminated_Total' : terminated_total or 0,
			'get_date_formate' : self.get_date_formate,
		}
		return docargs
		
