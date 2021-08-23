import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from operator import itemgetter

class ReportGuardsAttendance(models.AbstractModel):
	_name = 'report.sos_payroll.report_guardattendance'
	_description = 'SOS Guard Attendance Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def get_posts(self, data):
		date_from  = data['date_from']
		date_to  = data['date_to']
		post_obj = self.env['sos.post']
		post_ids  = data['post_ids']
		domain =[]
		
		if post_ids:
			post_ids = post_obj.search([('id', 'in', post_ids)])
		
		if not post_ids:
			center_ids = data['center_ids']
			if center_ids:
				domain = [('center_id', 'in', center_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
				posts_id = post_obj.search(domain)
				post_ids = posts_id
			
		if not post_ids:
			project_ids= data['project_ids']
			if project_ids:
				domain = [('project_id', 'in', project_ids),'|',('active','=',True),'&',('enddate' ,'>=',date_from ),('enddate', '<=', date_to)]
				posts_id = post_obj.search(domain)
				post_ids = posts_id		
		
		return post_ids
			
	def post_attendance_lines(self, post_id,data):
		res = {}
		att_line_obj = self.env['sos.guard.attendance']
		date_start  = data['date_from']
		date_stop  = data['date_to']
		post_id = post_id
		search_ids = [('name', '>=', date_start),('name', '<=', date_stop),('post_id', '=', post_id)]
		att_line_ids = att_line_obj.search(search_ids)
		if not att_line_ids:
			return []
				
		lines = self._get_att_lines(att_line_ids.ids, 'post')
		return lines
		
		
	def _get_att_lines(self, att_line_ids,ord_by):
		if not att_line_ids:
			return []		
		
		if not isinstance(att_line_ids, list):
			att_line_ids = [att_line_ids]
			
		monster ="""SELECT t.employee_id,t.post_id, emp.name as emp_name,partner.name,emp.code,gc.name contract,guard.bankacctitle,guard.bankacc,bank.name bank1_name,
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
			monster += """ group by t.employee_id,t.post_id,emp.name,partner.name,emp.code,gc.name,guard.bankacctitle,guard.bankacc,bank.name"""
		else:
			monster += """ group by t.post_id,t.employee_id,emp.name,partner.name,emp.code,gc.name,guard.bankacctitle,guard.bankacc,bank.name"""		
		try:
			self.env.cr.execute(monster, (tuple(att_line_ids),))
			res= self.env.cr.dictfetchall()
		except Exception:
			self.env.cr.rollback()
			raise		
		
		### Attendance Policy Code Here ###
		for r in res:
			paid_leaves = 0
			flag = True
						
			paid_ids = self.env['guards.leave.policy'].search([('post_id','=',r['post_id'])], order="from_days desc")
			if not paid_ids:
				post_rec = self.env['sos.post'].browse(r['post_id'])
				center_id = self.env['sos.center'].search([('id','=',post_rec.center_id.id)])
				project_id = self.env['sos.project'].search([('id','=',post_rec.project_id.id)])
				
				paid_ids = self.env['guards.leave.policy'].search([('center_id','=',center_id.id),('project_id','=',project_id.id),('post_id','=',False)], order="from_days desc")	
			paid_recs = paid_ids
			
			for paid_rec in paid_recs:
				if r['total'] >= paid_rec.from_days and flag:
					paid_leaves = paid_rec.leaves
					flag = False
			r['paid_leaves'] = paid_leaves
			r['total'] += paid_leaves	
		return res or []
		
		
	def get_guards(self, data):
		date_from  = data['date_from']
		date_to  = data['date_to']
		
		employee_obj = self.env['hr.employee']
		guard_posts_obj = self.env['sos.guard.post']
		domain = []
		
		employee_ids = data['employee_ids']
		if employee_ids:
			employee_ids = employee_obj.search([('id','in',employee_ids)])
		
		if not employee_ids:
			post_ids = data['post_ids']
			if post_ids:
				domain = [('post_id', 'in', post_ids),'|',('current','=',True),'&',('resigdate' ,'>=',date_from ),('resigdate', '<=', date_to)]
				search_ids = guard_posts_obj.search(domain)
				guards = guard_posts_obj.read(search_ids,['employee_id'])
				for guard in guards:
					employee_ids = ids.append(guard['employee_id'][0])
					
		if not employee_ids:
			center_ids = data['center_ids']
			if center_ids:
				domain = [('center_id', 'in', center_ids),'|',('current','=',True),'&',('resigdate' ,'>=',date_from ),('resigdate', '<=', date_to)]
				employee_ids = employee_obj.search(domain)
				
		if not employee_ids:
			project_ids = data['project_ids']
			if project_ids:
				domain = [('project_id', 'in', project_ids),'|',('current','=',True),'&',('resigdate' ,'>=',date_from ),('resigdate', '<=', date_to)]				
				employee_ids = employee_obj.search(domain)

		employees =employee_ids
		return employees
		
	
	def guard_attendance_lines(self, employee_id, data):
		att_line_obj = self.env['sos.guard.attendance']
		date_start  = data['date_from']
		date_stop  = data['date_to']
		domain = [('name', '>=', date_start),('name', '<=', date_stop),('employee_id', '=', employee_id)]
		
		att_line_ids = att_line_obj.search(domain)
		if not att_line_ids:
	 		return []
				
		lines = self._get_att_lines(att_line_ids.ids, 'guard')
		return lines	
		
		
	@api.model
	def _get_report_values(self, docids, data=None):
		group_by = data['form']['group_by'] and data['form']['group_by'] or False
		line_ids = []
		res = {}
		p_grand_total = 0 
		
		if group_by == 'posts':
			posts = self.get_posts(data['form'])
			for post in posts:
			
				p_total_present = 0
				p_total_extra = 0
				p_total_double = 0
				p_total_ex_double = 0
				p_total_absent = 0
				p_total_paid = 0
				p_total = 0
			
				att_recs = self.post_attendance_lines(post.id,data['form'])
				if att_recs:
					for att_rec in att_recs:
						p_total_present += att_rec['present'] or 0
						p_total_extra += att_rec['extra'] or 0
						p_total_double += att_rec['double'] or 0
						p_total_ex_double += att_rec['extra_double'] or 0 
						p_total_absent += att_rec['absent'] or 0
						p_total_paid += att_rec['paid_leaves'] or 0
						p_total += att_rec['total'] or 0
					
					p_grand_total += p_total or 0	
					line=({
						'post_name' : post.name, 
						'att_recs' : att_recs,
						'p_total_present' : p_total_present,
						'p_total_extra' : p_total_extra,
						'p_total_double' : p_total_double,
						'p_total_ex_double' : p_total_ex_double,
						'p_total_absent' : p_total_absent,
						'p_total_paid' : p_total_paid,
						'p_total' : p_total,
						})
					line_ids.append(line)	
			res = line_ids
			
		if group_by == 'guards':
			guards = self.get_guards(data['form'])
			for guard in guards:
				
				g_total_present = 0
				g_total_extra = 0
				g_total_double = 0
				g_total_ex_double = 0
				g_total_absent = 0
				g_total_paid = 0
				g_total = 0
			
				att_recs = self.guard_attendance_lines(guard.id,data['form'])
				if att_recs:
					for att_rec in att_recs:
						g_total_present += att_rec['present'] or 0
						g_total_extra += att_rec['extra'] or 0
						g_total_double += att_rec['double'] or 0
						g_total_ex_double += att_rec['extra_double'] or 0 
						g_total_absent += att_rec['absent'] or 0
						g_total_paid += att_rec['paid_leaves'] or 0
						g_total += att_rec['total'] or 0
					
					p_grand_total += g_total or 0	
					line=({
						'guard_name' : guard.name,
						'code' : guard.code,  
						'att_recs' : att_recs,
						'g_total_present' : g_total_present,
						'g_total_extra' : g_total_extra,
						'g_total_double' : g_total_double,
						'g_total_ex_double' : g_total_ex_double,
						'g_total_absent' : g_total_absent,
						'g_total_paid' : g_total_paid,
						'g_total' : g_total,
						})
					line_ids.append(line)	
			res = line_ids	
	
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_guardattendance')
		docargs = {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Post_Att" : res or False,
			"Guard_Att" : res or False,
			"Grand_Total" : p_grand_total or 0,
			"get_date_formate" : self.get_date_formate,
		}
		return docargs
