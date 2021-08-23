import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
	
#from odoo.tools.amount_to_text_en import amount_to_text
#from odoo.tools.amount_to_text_en import english_number



class ReportStaffDokkanSalarySheet(models.AbstractModel):
	_name = 'report.hr_payroll_ext.report_dokkan_staffsalarysheet'

	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	def get_staff_working_days(self,payslip_id=None,code=None):
		worked_day_obj = self.env['hr.payslip.worked_days']
		worked_day_id = worked_day_obj.search([('payslip_id','=',payslip_id),('code','=',code)])
		return worked_day_id.number_of_days

	def get_staff_lines(self,payslip_id,line_type=None,code=None):

		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
		amount =0
		if line_type == 'payslip_line':
			payslip_line_id = payslip_line_obj.search([('slip_id','=',payslip_id),('code','=',code)])
			amount = payslip_line_id.total or 0
		if line_type == 'input_line':
			input_id = payslip_input_obj.search([('payslip_id','=',payslip_id),('code','=',code)])
			amount=input_id.amount or 0
		return amount
		
	def get_salary_package_total(self,payslip_id=None,code=None):
		total = 0
		comp_2percent = 0
		comp_10percent = 0
		emp_10percent = 0
		total_gosi  = 0
		
		
		if code == 'total':
			basic = self.get_staff_lines(payslip_id,'payslip_line','BASIC')
			housing = self.get_staff_lines(payslip_id,'payslip_line','Housing')
			transport = self.get_staff_lines(payslip_id,'payslip_line','TRA')
			other = self.get_staff_lines(payslip_id,'payslip_line','OA')
			total = basic + housing + transport + other
			
			payslip = self.env['hr.payslip'].search([('id','=',payslip_id)])
			if payslip.employee_id.country_id.id != 192:
				comp_2percent = (basic + housing)*0.02
				total_gosi = comp_2percent
				
			if payslip.employee_id.country_id.id == 192:
				comp_2percent = (basic + housing)*0.02
				comp_10percent = (basic + housing)*0.10
				emp_10percent = (basic + housing)*0.10
				total_gosi = comp_2percent + comp_10percent + emp_10percent
				
			val = ({
				'total' : total,
				'comp_2percent' : comp_2percent,
				'comp_10percent' : comp_10percent,
				'emp_10percent' : emp_10percent,
				'total_gosi' : total_gosi,
				})				
		return val
		
	
	def amount_in_word(self, amount_total):
		number = '%.2f' % amount_total
		units_name = 'SR'
		list = str(number).split('.')
		start_word = english_number(int(list[0]))
		return ' '.join(filter(None, [start_word, units_name]))
		#return amount_to_text(amount_total,'en','SR')			

	@api.model
	def get_report_values(self, docsid, data=None):			
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
				
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']

		payslip_obj = self.env['hr.payslip']
		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
		
		### Local Variables to Get Totals ###
		basic = 0
		net = 0
		gross = 0
		arrear = 0
		bonus = 0
		trans = 0
		incentive = 0
		over_time = 0
		advance = 0
		fine =0
		other_deduction = 0
		housing = 0
		other_allow = 0
		gosi = 0
		wage = 0
		total = 0
		gosi_comp_2percent = 0
		gosi_comp_10percent = 0
		gosi_emp_10percent = 0
		gosi_emp_10percent = 0
		gosi_total = 0
		total_deduction = 0
		
		recs = []
		
		#all Departments
		departments = self.env['hr.department'].search([],order='code')	
		
		for department in departments:
			#Department Local Variables
			dept_basic = 0
			dept_net = 0
			dept_gross = 0
			dept_arrear = 0
			dept_bonus = 0
			dept_trans = 0
			dept_housing = 0
			dept_incentive = 0
			dept_over_time = 0
			dept_advance = 0
			dept_other_deduction = 0
			dept_other_allow = 0
			dept_gosi = 0
			dept_wage = 0
			dept_total = 0
			dept_gosi_comp_2percent = 0
			dept_gosi_comp_10percent = 0
			dept_gosi_emp_10percent = 0
			dept_gosi_total = 0
			dept_fine = 0
			dept_total_deduction = 0
			
			employees = self.env['hr.employee'].search([('department_id','=',department.id)])		
			payslips = payslip_obj.sudo().search([('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','in',employees.ids)],order='employee_id')
			
			if payslips:
				for payslip in payslips:
					dept_wage = dept_wage + payslip.contract_id.wage
					wage = wage + payslip.contract_id.wage
					line_ids = payslip_line_obj.search([('slip_id','=',payslip.id)])
					
					salary_package = self.get_salary_package_total(payslip.id,'total')
					
					
					dept_total = dept_total + salary_package['total']
					total = total + salary_package['total']
					
					dept_gosi_comp_2percent = dept_gosi_comp_2percent + salary_package['comp_2percent']
					gosi_comp_2percent = gosi_comp_2percent + salary_package['comp_2percent']
					
					dept_gosi_comp_10percent = dept_gosi_comp_10percent + salary_package['comp_10percent']
					gosi_comp_10percent = gosi_comp_10percent + salary_package['comp_10percent']
					
					dept_gosi_emp_10percent = dept_gosi_emp_10percent + salary_package['emp_10percent']
					gosi_emp_10percent = gosi_emp_10percent + salary_package['emp_10percent']
					
					dept_gosi_total = dept_gosi_total + salary_package['total_gosi']
					gosi_total = gosi_total + salary_package['total_gosi']
					
					for line_id in line_ids:
						if line_id.code == 'BASIC':
							dept_basic = line_id.total + dept_basic
							basic = line_id.total + basic
						elif line_id.code == 'NET':
							dept_net = line_id.total + dept_net
							net = line_id.total + net
						elif line_id.code == 'GROSS':
							dept_gross = line_id.total + dept_gross
							gross = line_id.total + gross
						elif line_id.code == 'TRA':
							dept_trans = line_id.total + dept_trans
							trans = line_id.total + trans
						elif line_id.code == 'Housing':
							dept_housing = line_id.total + dept_housing
							housing = line_id.total + housing
						elif line_id.code == 'OA':
							dept_other_allow = line_id.total + dept_other_allow
							other_allow = line_id.total + other_allow												
						else:
							dummy = 0
						
					input_ids = payslip_input_obj.search([('payslip_id','=',payslip.id)])
					
					for input_id in input_ids:
						if input_id.code == 'ARS':
							dept_arrear = input_id.amount + dept_arrear
							arrear = input_id.amount + arrear
						elif input_id.code == 'BNS':
							dept_bonus = input_id.amount + dept_bonus 
							bonus = input_id.amount + bonus 
						elif input_id.code == 'INCTV':
							dept_incentive = input_id.amount + dept_incentive
							incentive = input_id.amount + incentive
							dept_over_time =  input_id.amount + dept_over_time
							over_time = input_id.amount + over_time
						elif input_id.code == 'OT':
							dept_over_time = input_id.amount + dept_over_time
							over_time = input_id.amount + over_time
						elif input_id.code == 'ADV' or input_id.code == 'LOAN':
							dept_advance = dept_advance + input_id.amount
							dept_total_deduction = dept_total_deduction + input_id.amount
							total_deduction = total_deduction + input_id.amount
							advance = advance + input_id.amount
						elif input_id.code == 'ODE':
							dept_other_deduction = input_id.amount + dept_other_deduction
							other_deduction = input_id.amount + other_deduction
						elif input_id.code == 'FINE':
							dept_fine = input_id.amount + dept_fine
							dept_total_deduction = dept_total_deduction + input_id.amount
							total_deduction = total_deduction + input_id.amount
							fine = input_id.amount + fine		
						else:
							dummy = 0
						
				recs.append({
					'payslips' : payslips,
					'department' : department.name,
					'dept_basic' : dept_basic,
					'dept_net' : dept_net,
					'dept_gross' : dept_gross,
					'dept_arrear' : dept_arrear,
					'dept_bonus' : dept_bonus,
					'dept_trans' : dept_trans,
					'dept_incentive' : dept_incentive,
					'dept_over_time' : dept_over_time,
					'dept_advance' :  dept_advance,
					'dept_other_deduction' : dept_other_deduction,
					'dept_housing' : dept_housing,
					'dept_other_allow' : dept_other_allow,
					'dept_total' : dept_total,
					'dept_gosi_comp_2percent' : dept_gosi_comp_2percent,
					'dept_gosi_comp_10percent' : dept_gosi_comp_10percent,
					'dept_gosi_emp_10percent' : dept_gosi_emp_10percent,
					'dept_gosi_total' : dept_gosi_total,
					'dept_fine' : dept_fine,
					'dept_total_deduction' : dept_total_deduction,
					})	
		
		report = self.env['ir.actions.report']._get_report_from_name('hr_payroll_ext.report_dokkan_staffsalarysheet')
		slips = self.env['hr.payslip']
		
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'data': data['form'],
			'docs': slips,
			'time': time,
			'Payslip': recs,
			'Working_Days' : self.get_staff_working_days,
			'Lines' : self.get_staff_lines,
			'BASIC': basic,
			'NET' : net,
			'GROSS' : gross,
			'ARREAR' : arrear,
			'TRANS': trans,
			'BONUS' : bonus,
			'INCENTIVE' : incentive,
			'OVER_TIME' : over_time,
			'ADVANCE' : advance,
			'FINE' : fine,
			'OTHER_DEDUCTION' : other_deduction,
			'get_date_formate' : self.get_date_formate,
			'amount_in_word': self.amount_in_word,
			'HOUSING': housing,
			'OTHER_ALLOW' : other_allow,
			'SALARY_PACKAGE' : self.get_salary_package_total,
			'TOTAL' : total,
			'COMP_2PERCENT' : gosi_comp_2percent,
			'COMP_10PERCENT' : gosi_comp_10percent,
			'EMP_10PERCENT' : gosi_emp_10percent,
			'GOSI_TOTAL' : gosi_total,
			'TOTAL_DEDUCTION' : total_deduction,
		}
		
		return docargs
		
			
	#***** Excel Report ***** sea_green#
	@api.multi
	def make_excel(self, data):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		#***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Salary Sheet")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour periwinkle;")
		style_table_header2 = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_table_totals = xlwt.easyxf("font:height 220; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		
		style_department = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour light_turquoise;")
		style_department_total = xlwt.easyxf("font:height 170; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		style_department_total_name = xlwt.easyxf("font:height 170; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		
		style_payslip_data = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")
		style_payslip_data_name = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		
		#col width
		second_col = worksheet.col(1)
		second_col.width = 256 * 35
		
		seventeen_col = worksheet.col(16)
		seventeen_col.width = 256 * 20
		
		worksheet.write_merge(0, 1, 0, 20,"Salary Sheet Report", style = style_title)
		row = 3
		col = 0
		
		#***** Table Heading *****#
		table_header = ['S.No','Name','No.','Joining Date','Basic Salary','Housing','Transport','COLA','Total','M. Days','Absence','Net','2% Co.','10% Co.','10% Emp.','Total Gosi','Deductions','Installment','Total Deductions','OT/Additional','Net Wage']
		for i in range(21):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1
		
		row = 4
		col = 0	
		
		#***** Fetching Data from View *****#	
		dta = self.get_report_values(None,data)
		recs = dta['Payslip']
		
		
		#***** Table Data *****#
		for rec in recs:
			worksheet.write_merge(row, row, 0, 20,rec.get('department').upper(), style=style_department)
			row +=1
			col = 0
			
			i = 1
			for payslip in rec.get('payslips'):
				salary_package = self.get_salary_package_total(payslip.id,'total')
			
				col = 0
				worksheet.write(row,col,i,style=style_payslip_data_name)
				col += 1
				worksheet.write(row,col,payslip.employee_id.english_name, style=style_payslip_data_name)
				col += 1
				worksheet.write(row,col,payslip.employee_id.code, style=style_payslip_data_name)
				col += 1
				worksheet.write(row,col,self.get_date_formate(payslip.employee_id.joining_date), style=style_payslip_data_name)
				col += 1
				
				#format(purchase,'.2f' or 0.00) or ''
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','BASIC'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','Housing'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','TRA'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','OA'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(salary_package.get('total'),',.2f'), style=style_payslip_data)
				col += 1
				
				worksheet.write(row,col,self.get_staff_working_days(payslip.id,'MAX'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,'-', style=style_payslip_data)
				col += 1
				worksheet.write(row,col,self.get_staff_working_days(payslip.id,'WORK100'), style=style_payslip_data)
				col += 1
				
				
				worksheet.write(row,col,format(salary_package.get('comp_2percent'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(salary_package.get('comp_10percent'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(salary_package.get('emp_10percent'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(salary_package.get('total_gosi'),',.2f'), style=style_payslip_data)
				col += 1
				
				adv = 0
				adv = (self.get_staff_lines(payslip.id,'input_line','ADV') + self.get_staff_lines(payslip.id,'input_line','LOAN'))
				
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'input_line','FINE'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(adv,',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format((self.get_staff_lines(payslip.id,'input_line','FINE') + self.get_staff_lines(payslip.id,'input_line','LOAN') + self.get_staff_lines(payslip.id,'input_line','ADV')),',.2f'), style=style_payslip_data)
				col += 1
				
				
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','OT'),',.2f'), style=style_payslip_data)
				col += 1
				worksheet.write(row,col,format(self.get_staff_lines(payslip.id,'payslip_line','NET'),',.2f'), style=style_payslip_data)
				col += 1
			
				row +=1
				col = 0
				i +=1
			
			#department toals
			col = 3
			worksheet.write_merge(row, row, 0, col,'SUB TOTAL FOR ' + rec.get('department').upper(), style=style_department_total_name)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_basic'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_housing'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_trans'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_other_allow'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_total'),',.2f'), style=style_department_total)
			col +=1
			
			
			worksheet.write(row,col,'', style=style_department_total)
			col +=1
			worksheet.write(row,col,'', style=style_department_total)
			col +=1
			worksheet.write(row,col,'', style=style_department_total)
			col +=1
			
			worksheet.write(row,col,format(rec.get('dept_gosi_comp_2percent'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_gosi_comp_10percent'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_gosi_emp_10percent'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_gosi_total'),',.2f'), style=style_department_total)
			col +=1
			
			
			worksheet.write(row,col,format(rec.get('dept_fine'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_advance'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_total_deduction'),',.2f'), style=style_department_total)
			col +=1
			
			
			worksheet.write(row,col,format(rec.get('dept_over_time'),',.2f'), style=style_department_total)
			col +=1
			worksheet.write(row,col,format(rec.get('dept_net'),',.2f'), style=style_department_total)
			col +=1
			
			
			row +=1
			col = 0
			
			
		#Overall Totals of Salary
		col = 3
		worksheet.write_merge(row, row, 0, col,'Grand Total Salary', style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('BASIC'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('HOUSING'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('TRANS'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('OTHER_ALLOW'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('TOTAL'),',.2f'), style=style_table_totals)
		col +=1
		
		worksheet.write(row,col,'', style=style_table_totals)
		col +=1
		worksheet.write(row,col,'', style=style_table_totals)
		col +=1
		worksheet.write(row,col,'', style=style_table_totals)
		col +=1
		
		worksheet.write(row,col,format(dta.get('COMP_2PERCENT'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('COMP_10PERCENT'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('EMP_10PERCENT'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('GOSI_TOTAL'),',.2f'), style=style_table_totals)
		col +=1
		
		worksheet.write(row,col,format(dta.get('FINE'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('ADVANCE'),',.2f'), style=style_table_totals)
		col +=1
		worksheet.write(row,col,format(dta.get('TOTAL_DEDUCTION'),',.2f'), style=style_table_totals)
		col +=1
		
		worksheet.write(row,col,format(dta.get('OVER_TIME'),',.2f'), style=style_table_totals)
		col +=1
		
		worksheet.write(row,col,format(dta.get('NET'),',.2f'), style=style_table_totals)
		col +=1
		
		row +=1
		col = 0
		
		
		#Signature Row	
		row +=3
		col = 1
		worksheet.write(row,col,'Check By:')
		col = 16
		worksheet.write(row,col,'Approved By:')
		
		row +=5
		col = 1
		worksheet.write(row,col,'Fida Hussain Ali Khan',style=style_department)
		
		col = 16
		worksheet.write(row,col,'Ammar Waganah',style=style_department)
		
		
		row +=1
		col = 1
		worksheet.write(row,col,'Finance Manager',style=style_department)
		
		col = 16
		worksheet.write(row,col,'Executive Manager',style=style_department)
							
		
		
		file_data = io.BytesIO()		
		workbook.save(file_data)		
		return file_data.getvalue()		
		
		

