import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class GuardsJoinTerminationReport(models.AbstractModel):
	_name = 'report.sos.report_guards_jointermination'
	_description = 'SOS Guards Join Termination Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def get_joined_guards(self,data=None):
		date_from = data['form']['date_from']
		date_to= data['form']['date_to']
		order_by = data['form']['order_by']	
				
		center_ids =self.env['sos.center'].search([])
		project_ids = self.env['sos.project'].search([])
		domain = [('project_id','in',project_ids.ids),('center_id','in',center_ids.ids),('appointmentdate','>=',date_from),('appointmentdate','<=',date_to)]
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
			
		guards = self.env['hr.employee'].sudo().search(domain,order=order_by)
		res = []
		
		for guard in guards:
			res.append({
				'name': guard.name,
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
		return res
		
	def get_terminated_guards(self,data=None):
		date_from = data['form']['date_from']
		date_to= data['form']['date_to']
		order_by = data['form']['order_by']
					
		center_ids = self.env['sos.center'].search([])
		project_ids = self.env['sos.project'].search([])

		domain = [('project_id','in',project_ids.ids),('center_id','in',center_ids.ids),('todate','>=',date_from),('todate','<=',date_to),('to_reason','in',['terminate','escape'])]

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
		
		guard_posts = self.env['sos.guard.post'].sudo().search(domain,order=order_by)
		res = []
			
		for guard_post in guard_posts:
			res.append({
				'name': guard_post.employee_id.name,
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
		return res	
	
	@api.model
	def _get_report_values(self, docids, data=None):		
		center_current = 0
		center_unknown = 0
		center_escaped = 0
		center_joined = 0
		center_terminated = 0
		center_transfered = 0
		
		project_current = 0
		project_unknown = 0
		project_escaped = 0
		project_joined = 0
		project_terminated = 0
		project_transfered = 0
		
		center_res = []
		project_res = []
		
		## For Centers ##
		center_ids = self.env['sos.center'].search([])
		project_ids = self.env['sos.project'].search([])
		
		for center in center_ids:
			emp_count = self.env['hr.employee'].sudo().search_count([('center_id', '=', center.id),('project_id', 'in', project_ids.ids),('current', '=', True)])
			
			self.env.cr.execute("select SUM(CASE WHEN to_reason is Null THEN 1 ELSE 0 END) AS unknown, \
					SUM(CASE WHEN to_reason = 'transfer' THEN 1 ELSE 0 END) AS transfer, \
					SUM(CASE WHEN to_reason = 'terminate' THEN 1 ELSE 0 END) AS terminate, \
					SUM(CASE WHEN to_reason = 'escape' THEN 1 ELSE 0 END) AS escape \
					from sos_guard_post j, sos_post p where j.post_id = p.id \
					and p.center_id = %s and j.todate >= %s and j.todate <= %s and j.project_id in %s",(center.id,data['form']['date_from'],data['form']['date_to'],tuple(project_ids.ids)))
			center_shifting = self.env.cr.dictfetchall()[0]

			self.env.cr.execute("select count(*) as joined from hr_employee e, hr_guard g where e.guard_id = g.id and center_id = %s and \
				appointmentdate >= %s and appointmentdate <= %s and project_id in %s",(center.id,data['form']['date_from'],data['form']['date_to'],tuple(project_ids.ids)))
			center_joining = self.env.cr.dictfetchall()[0]
			
			center_res.append({
				'name': center.name,
				'current': emp_count or 0,
				'terminated': center_shifting['terminate'] or '-',
				'transfered': center_shifting['transfer'] or '-',
				'escaped': center_shifting['escape'] or '-',
				'joined': center_joining['joined'] or '-',
				'unknown': center_shifting['unknown'] or '-',
			})
			
			center_current += emp_count or 0
			center_terminated += center_shifting['terminate'] or 0
			center_escaped += center_shifting['escape'] or 0
			center_transfered += center_shifting['transfer'] or 0
			center_unknown += center_shifting['unknown'] or 0
			center_joined += center_joining['joined'] or 0
						
		
		##For Projects ##
		project_ids = self.env['sos.project'].search([])
		center_ids =self.env['sos.center'].search([])
	
		for project in project_ids:
			emp_count = self.env['hr.employee'].search_count([('project_id', '=', project.id),('center_id', 'in', center_ids.ids),('current', '=', True)])

			self.env.cr.execute("select SUM(CASE WHEN to_reason is Null THEN 1 ELSE 0 END) AS unknown, \
					SUM(CASE WHEN to_reason = 'transfer' THEN 1 ELSE 0 END) AS transfer, \
					SUM(CASE WHEN to_reason = 'terminate' THEN 1 ELSE 0 END) AS terminate, \
					SUM(CASE WHEN to_reason = 'escape' THEN 1 ELSE 0 END) AS escape \
					from sos_guard_post j, sos_post p where j.post_id = p.id and \
					j.project_id = %s and j.todate >= %s and j.todate <= %s and p.center_id in %s",(project.id,data['form']['date_from'],data['form']['date_to'],tuple(center_ids.ids)))
			project_shifting = self.env.cr.dictfetchall()[0]

			self.env.cr.execute("select count(*) as joined from hr_employee e, hr_guard g where e.guard_id=g.id and project_id = %s and \
				appointmentdate >= %s and appointmentdate <= %s and center_id in %s",(project.id,data['form']['date_from'],data['form']['date_to'],tuple(center_ids.ids)))
			project_joining = self.env.cr.dictfetchall()[0]
			
			project_res.append({
				'name': project.name,
				'current': emp_count or 0,
				'terminated': project_shifting['terminate'] or '-',
				'transfered': project_shifting['transfer'] or '-',
				'escaped': project_shifting['escape'] or '-',
				'joined': project_joining['joined'] or '-',
				'unknown': project_shifting['unknown'] or '-',
			})
			
			project_current += emp_count
			project_terminated += project_shifting['terminate'] or 0
			project_escaped += project_shifting['escape'] or 0
			project_transfered += project_shifting['transfer'] or 0
			project_unknown += project_shifting['unknown'] or 0
			project_joined += project_joining['joined'] or 0
			
		jj = self.get_joined_guards(data)				
		tt = self.get_terminated_guards(data)
		
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_guards_jointermination')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Center_Guards' : center_res or False,
			'Center_Current' : center_current,
			'Center_Unknown' : center_unknown,
			'Center_Escaped' : center_escaped,
			'Center_Joined' : center_joined,
			'Center_Terminated' : center_terminated,
			'Center_Transfered' : center_transfered,
			
			'Project_Guards' : project_res or False,
			'Project_Current' : project_current,
			'Project_Unknown' : project_unknown,
			'Project_Escaped' : project_escaped,
			'Project_Joined' : project_joined,
			'Project_Terminated' : project_terminated,
			'Project_Transfered' : project_transfered,
			'Joined_Guards' :  jj or False,
			'Terminated_Guards' : tt or False,
			'get_date_formate' : self.get_date_formate,
		}
