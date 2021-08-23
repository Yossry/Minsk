import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class ABLIncentive(models.AbstractModel):
	_name = 'report.sos_payroll.report_ablincentive'
	_description = 'ABL Incentive Report'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
		
	def get_post_name(self,payslip_id,employee_id):
		work_obj = self.env['guards.payslip.worked_days']
		work_id = work_obj.search([('payslip_id','=',payslip_id),('project_id','=',26),('employee_id','=',employee_id)])
		return work_id[0].post_id.name
	
		
	def get_working_days(self,payslip_id,employee_id):
		number_of_days = 0
		work_obj = self.env['guards.payslip.worked_days']
		work_ids = work_obj.search([('payslip_id','=',payslip_id),('project_id','=',26),('employee_id','=',employee_id)])
		for work_id in work_ids:
			number_of_days += work_id.number_of_days
		return number_of_days


	@api.model
	def _get_report_values(self, docids, data=None):
		total_amount = 0		
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		payslip_line_obj = self.env['guards.payslip.line']
		payslip_line_ids = payslip_line_obj.search([('date_from','>=',date_from),('date_to','<=',date_to),('code','=','ATTINC')],order='post_id')
		
		for line_id in payslip_line_ids:
			total_amount = (line_id.total) + total_amount

		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_ablincentive')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'PayslipLines': payslip_line_ids,
			'Days' : self.get_working_days,
			'Post' : self.get_post_name,
			'get_date_formate' : self.get_date_formate,
			'total_amount' : total_amount
		}
		return docargs
