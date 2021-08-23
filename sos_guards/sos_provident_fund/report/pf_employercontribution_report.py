import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models, _
import pytz, datetime
from dateutil import tz
from odoo import tools
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class ReportPFEmployerContribution(models.AbstractModel):
	_name = 'report.sos_provident_fund.report_pf_employercontribution'
	_description = 'PF Employer Contribution'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate[:10],'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		
		project_ids = data['form']['project_ids'] and data['form']['project_ids'] or False
		center_ids = data['form']['center_ids'] and data['form']['center_ids'] or False
		post_ids = data['form']['post_ids'] and data['form']['post_ids'] or False
		guard_ids = data['form']['guard_ids'] and data['form']['guard_ids'] or False

		report_category = data['form']['category'] and data['form']['category'] or False
		from_resign_date = data['form']['from_resign_date'] and data['form']['from_resign_date'] or False
		to_resign_date = data['form']['to_resign_date'] and data['form']['to_resign_date'] or False

		if not report_category:
			raise UserError("Please Select the Report Cateogry, Current Employee or Inactive Employee")
		
		data_recs = []
		res = {}
		
		#Projects
		if project_ids:
			for project_id in project_ids:
				emp_ids = False
				recs = False
				total = 0
				
				project = self.env['sos.project'].search([('id','=',project_id)])
				post_ids = self.env['sos.post'].search([('project_id','=', project_id),'|',('active','=',True),'&',('enddate' ,'>=', data['form']['date_from'] ),('enddate', '<=',  data['form']['date_to'])])

				if report_category == 'Current':
					emp_ids = self.env['hr.employee'].search([('current_post_id','in',post_ids.ids),('current','=',True)])
				if report_category == 'Inactive' and from_resign_date and to_resign_date:
					emp_ids = self.env['hr.employee'].search([('current_post_id','in',post_ids.ids),('current','=',False),('resigdate','>=',from_resign_date),('resigdate','<=',to_resign_date)])
				
				if emp_ids:
					#Detail
					self.env.cr.execute("""select e.code as emp_code,e.name as guard_name,g.cnic as cnic,g.current as status,sum(abs(pl.amount)) as amount from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id group by e.code,e.name,g.cnic,g.current""" ,(date_from,date_to,tuple(emp_ids.ids),))
					recs = self.env.cr.dictfetchall()
					
					#Total
					self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" ,(date_from,date_to,tuple(emp_ids.ids),))
					total = self.env.cr.dictfetchall()[0]['total']
					
					if recs:
						project_line =({
							'project' : project.name,
							'recs' : recs,
							'total' : total,
							})
						data_recs.append(project_line)
		#Centers		
		elif center_ids:
			for center_id in center_ids:
				emp_ids = False
				recs = False
				center = self.env['sos.center'].search([('id','=',center_id)])
				post_ids = self.env['sos.post'].search([('center_id','=', center_id),'|',('active','=',True),'&',('enddate' ,'>=', data['form']['date_from'] ),('enddate', '<=',  data['form']['date_to'])])

				if report_category == 'Current':
					emp_ids = self.env['hr.employee'].search([('current_post_id', 'in', post_ids.ids), ('current', '=', True)])
				if report_category == 'Inactive' and from_resign_date and to_resign_date:
					emp_ids = self.env['hr.employee'].search([('current_post_id', 'in', post_ids.ids), ('current', '=', False),('resigdate', '>=', from_resign_date), ('resigdate', '<=', to_resign_date)])

				if emp_ids:
					#Detail
					self.env.cr.execute("""select e.code as emp_code,e.name as guard_name,g.cnic as cnic,g.current as status,sum(abs(pl.amount)) as amount from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id group by e.code,e.name,g.cnic,g.current""" ,(date_from,date_to,tuple(emp_ids.ids),))
					recs = self.env.cr.dictfetchall()
					
					#Total
					self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" ,(date_from,date_to,tuple(emp_ids.ids),))
					total = self.env.cr.dictfetchall()[0]['total']
					
					if recs:
						project_line =({
							'project' : center.name,
							'recs' : recs,
							'total' : total,
							})
						data_recs.append(project_line)
		#Posts		
		elif post_ids:
			for post_id in post_ids:
				emp_ids = False
				recs = False
				post = self.env['sos.post'].search([('id','=',post_id)])

				if report_category == 'Current':
					emp_ids = self.env['hr.employee'].search([('current_post_id', 'in', post_ids.ids), ('current', '=', True)])
				if report_category == 'Inactive' and from_resign_date and to_resign_date:
					emp_ids = self.env['hr.employee'].search([('current_post_id', 'in', post_ids.ids), ('current', '=', False),('resigdate', '>=', from_resign_date), ('resigdate', '<=', to_resign_date)])

				if emp_ids:
					#Detail
					self.env.cr.execute("""select e.code as emp_code,e.name as guard_name,g.cnic as cnic,g.current as status,sum(abs(pl.amount)) as amount from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id group by e.code,e.name,g.cnic,g.current""" ,(date_from,date_to,tuple(emp_ids.ids),))			
					recs = self.env.cr.dictfetchall()
					
					#Total
					self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id in %s and pl.employee_id = e.id and e.guard_id = g.id""" ,(date_from,date_to,tuple(emp_ids.ids),))
					total = self.env.cr.dictfetchall()[0]['total']
					
					if recs:
						project_line =({
							'project' : post.name,
							'recs' : recs,
							'total' : total,
							})
						data_recs.append(project_line)

		elif guard_ids:
			for guard_id in guard_ids:
				emp_ids = False
				recs = False
				emp_id = self.env['hr.employee'].search([('id','=',guard_id),'|',('current','=',True),('current','=',False)])
				
				#Detail
				self.env.cr.execute("""select e.code as emp_code,e.name as guard_name,g.cnic as cnic,g.current as status,sum(abs(pl.amount)) as amount from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
					where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id = %s and pl.employee_id = e.id and e.guard_id = g.id group by e.code,e.name,g.cnic,g.current""" ,(date_from,date_to,guard_id))
				recs = self.env.cr.dictfetchall()
				
				#Total
				self.env.cr.execute("""select sum(abs(pl.amount)) as total from guards_payslip_line pl,guards_payslip p,hr_employee e,hr_guard g 
				where pl.code='GPROF' and pl.date_from >=%s and pl.date_to <=%s and pl.slip_id = p.id and pl.employee_id = %s and pl.employee_id = e.id and e.guard_id = g.id""" ,(date_from,date_to,guard_id))
				total = self.env.cr.dictfetchall()[0]['total']
				
				if recs:
					project_line =({
						'project' : emp_id.name,
						'recs' : recs,
						'total' : total,
						})
					data_recs.append(project_line)
		else:
			raise UserError(_("You must select any of the input"))

		res = data_recs		
		report = self.env['ir.actions.report']._get_report_from_name('sos_provident_fund.report_pf_employercontribution')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"recs": data_recs or False,
			"get_date_formate" : self.get_date_formate,
		}