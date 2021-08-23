import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class ProjectsSalaryAdvice(models.AbstractModel):
	_name = 'report.sos_payroll.report_projectssalary_advice'
	_description = 'Projec Salary Advice Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	@api.model
	def _get_report_values(self, docids, data=None):
		invoice_id =  data['form']['advice_id'] and data['form']['advice_id'][0] or False
		total_advised = 0
		
		payslip_obj = self.env['guards.payslip']
		project_obj = self.env['sos.project']

		self.env.cr.execute("select distinct project_id from guards_payslip where advice_id = %s" %(invoice_id))
		projects = self.env.cr.dictfetchall()
		res = []

		for project in projects:
			advised = 0
			project_id = project_obj.browse([project['project_id']])[0]
			
			self.env.cr.execute("select sum(t.total) as total from guards_payslip pl, guards_payslip_line t where t.slip_id = pl.id and t.code='NET' and pl.project_id = %s and pl.advice_id = %s", (project_id.id,invoice_id))
			lines = self.env.cr.dictfetchall()
			advised = lines[0]['total']
			
			total_advised += advised
			
			res.append({
				'name': project_id.name,
				'advised': advised or 0,			
			})

		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_projectssalary_advice')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Projects' : res,
			'Total_Advised' : total_advised or 0,
			'get_date_formate' : self.get_date_formate,
		}
		
