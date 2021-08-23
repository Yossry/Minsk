import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _


class GuardsMBLDeduction(models.AbstractModel):
	_name = 'report.sos_payroll.report_mbldeduction'
	_description = 'MBL Deduction Report'

	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
		
	def get_deposited_amount(self,employee_id):
		
		self.env.cr.execute("select sum(amount) as amount from guards_payslip_line where code in ('MBLPC','MBLD') and salary_rule_id in (146,149) and employee_id=%s" %(employee_id))
		amount = self.env.cr.dictfetchall()[0]['amount'] or 0
		return abs(amount)
		 

	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		total_amt = 0
		total_deposited = 450
		pro_total = 0
		line_ids = []
		res = {} 
		
		### Calculating the Project Wise Total###
		self.env.cr.execute ("select p.name as name,round(sum(pl.amount)) as amount from guards_payslip_line pl, sos_project p \
			where pl.project_id = p.id and pl.code in ('MBLPC','MBLD') and pl.date_from = %s  and pl.date_to =%s  group by p.name", (date_from,date_to));
		project_dict = self.env.cr.dictfetchall()
		if project_dict:
			for p in project_dict:
				pro_total = pro_total + abs(p['amount']) or 0
		
		payslip_lines = self.env['guards.payslip.line'].search([('code','in',('MBLPC','MBLD')),('salary_rule_id','in',(146,149)),('date_from','=',date_from),('date_to','=',date_to)],order='project_id,post_id')
		for payslip_line in payslip_lines:
			total_amt = total_amt + abs(payslip_line.amount)
			deposit_amt = self.get_deposited_amount(payslip_line.employee_id.id)
			
			line=({
				'ref' : payslip_line.employee_id.code,
				'name' : payslip_line.employee_id.name,
				'appoint_date' : payslip_line.employee_id.appointmentdate,
				'project' : payslip_line.project_id.name,
				'center' : payslip_line.employee_id.center_id.name,
				'post' : payslip_line.post_id.name,
				'amount' : payslip_line.amount or 0,
				'deposit_amount' : deposit_amt or 0,
				})
			line_ids.append(line)
		res = line_ids

		report = self.env['ir.actions.report']._get_report_from_name('sos_payroll.report_mbldeduction')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Project' : project_dict,
			'PayslipLines' : res,
			'get_deposited_amount' : self.get_deposited_amount,
			'Total': total_amt,
			'TotalDeposited' : total_deposited,
			'Pro_Total' : pro_total,
			'get_date_formate' : self.get_date_formate,
		}
		return docargs
		
