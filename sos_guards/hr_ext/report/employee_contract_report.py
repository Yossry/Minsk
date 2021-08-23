import pdb
import time
from datetime import datetime, timedelta
from odoo import api, models

class ReportEmployeeContract(models.AbstractModel):
	_name = 'report.hr_ext.report_employeecontract'
	_description = 'Employee Contract Report'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):	
		company_id = data['form']['company_id'] and data['form']['company_id'][0]
		employee_status = data['form']['employee_status'] and data['form']['employee_status'] or False
		segment_id = data['form']['segment_id'] and data['form']['segment_id'][0] or False
		sub_segment_id = data['form']['sub_segment_id'] and data['form']['sub_segment_id'][0] or False
		
		
		employees = False
		contract_lines = []
		res = {}
		
		if segment_id and sub_segment_id and employee_status =='Active':
			domain = [('segment_id','=',segment_id),('sub_segment_id','=',sub_segment_id),('active','=',True)]
		
		if segment_id and not sub_segment_id:
			domain = [('segment_id','=',segment_id),('active','=',True)]
		
		if not segment_id and not sub_segment_id:
			domain = [('active','=',True),('department_id','!=', 29)] #29--> Security Guards 		
			
		employees = self.env['hr.employee'].search(domain)
		
		if employees:
			for employee in employees:
				contract = self.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')])
				line=({
					'name' : employee.name,
					'code' :  employee.code,
					'department' :  employee.department_id and employee.department_id.name or False,
					'segment' : employee.segment_id and employee.segment_id.name or False,
					'sub_segment' : employee.sub_segment_id and employee.sub_segment_id.name or False,
					'date_start' : contract and contract.date_start or '-',
					'wage' : contract and contract.wage or '-',
					'house_rent_allowance' : contract and contract.house_rent_allowance or '-',
					'transportation_allowance' : contract and contract.transportation_allowance or '-',
					'mobile_allowance' : contract and contract.mobile_allowance or '-',
					'fuel_allowance' : contract and contract.fuel_allowance or '-',
					'food_allowance' : contract and contract.food_allowance or '-',
					'special_allowance' : contract and contract.special_allowance or '-',
					'bike_maintenance_allowance' : contract and contract.bike_maintenance_allowance or '-',
					'out_station_allowance' : contract and contract.out_station_allowance or '-',
					'supplementary_allowance' : contract and contract.supplementary_allowance or '-',
					'gross_salary' : contract and contract.gross_salary or '-',
					})
				contract_lines.append(line)	
			res = contract_lines
		
		
			
		#if employees:	
		#	contract_ids = self.env['hr.contract'].search([('employee_id','in',employees.ids),('state','=', 'open')], order="department_id")
		
		report = self.env['ir.actions.report']._get_report_from_name('hr_ext.report_employeecontract')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Contracts' : res or False,
			'get_date_formate' : self.get_date_formate,
		}
		return docargs

