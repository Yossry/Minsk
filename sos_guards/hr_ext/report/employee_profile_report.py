import time
from datetime import datetime, timedelta
from odoo import api, models
import pdb


class ReportEmployeeProfile(models.AbstractModel):
	_name = 'report.hr_ext.report_employeeprofile'
	_description = 'Employee Profile Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_employee_contract(self,employee_id):
		contract_id = self.env['hr.contract'].search([('employee_id','=',employee_id),('state','!=', 'done')], limit=1, order='date_start desc')
		return contract_id or False
	
	def get_terminate_reason(self,employee_id):
		term_id = False
		term_id = self.env['hr.employee.termination'].search([('employee_id','=',employee_id)])
		if term_id:
			reason = term_id.reason_id.name or '-'
		else:
			reason = '-'	
		return reason
	
	@api.model
	def get_report_values(self, docsid, data=None):					
		company_id = data['form']['company_id'] and data['form']['company_id'][0]
		emp_status = data['form']['emp_status']

		if emp_status == 'active':
			employee_ids = self.env['hr.employee'].search([('company_id','=',company_id),('active','=', True)], order="id")		
		
		if emp_status == 'inactive':
			employee_ids = self.env['hr.employee'].search([('company_id','=',company_id),('active','=', False)], order="id")
			
		if emp_status == 'both':
			employee_ids = self.env['hr.employee'].search([('company_id','=',company_id)], order="id")		
			
		report = self.env['ir.actions.report']._get_report_from_name('hr_ext.report_employeeprofile')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Employee' : employee_ids or False,
			'get_employee_contract' : self.get_employee_contract,
			'get_terminate_reason' : self.get_terminate_reason,
			'get_date_formate' : self.get_date_formate,
		}
		return docargs
		
		
		
		
		
		
		

