import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, fields, models, _
# from odoo.tools.amount_to_text_en import amount_to_text
# from odoo.tools.amount_to_text_en import english_number

class ReportStaffGrossSalarySheet(models.AbstractModel):
	_name = 'report.sos.report_staff_gross_salarysheet'
	_description = 'Staff Gross Salary Sheet Report'

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
	
	def amount_in_word(self, amount_total):
		number = '%.2f' % amount_total
		units_name = 'SR'
		list = str(number).split('.')
		start_word = english_number(int(list[0]))
		return ' '.join(filter(None, [start_word, units_name]))
		#return amount_to_text(amount_total,'en','SR')			

	@api.model
	def _get_report_values(self, docids, data=None):
				
		date_from = data['form']['date_from']
		date_to = data['form']['date_to']
		report_required = data['form']['report_required'] or False
		segment_wise = data['form']['segment_wise'] or False

		payslip_obj = self.env['hr.payslip']
		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
		
		### Local Variables to Get Totals ###
		net = 0
		basic = 0
		gross = 0
		arrear = 0
		bonus = 0
		mobile = 0
		food = 0
		trans = 0
		incentive = 0
		over_time = 0
		advance = 0
		
		housing = 0
		wage = 0
		fuel = 0
		bike = 0
		medical = 0
		out_station = 0
		special_allw = 0
		
		recs = []
		
		#IF HEAD OFFICE
		if report_required == 'headoffice':
			departments = self.env['hr.department'].search([('id','!=',29)]) #29--->Guarding	
		
			for department in departments:
				#Department Local Variables
				dept_net = 0
				dept_basic = 0
				dept_gross = 0
				dept_arrear = 0
				dept_bonus = 0
				dept_mobile = 0
				dept_food = 0
				dept_trans = 0
				dept_incentive = 0
				dept_over_time = 0
				dept_advance = 0

				dept_housing = 0
				dept_wage = 0
				dept_fuel = 0
				dept_bike = 0
				dept_medical = 0
				dept_out_station = 0
				dept_special_allw = 0
				
				if segment_wise == 'yes':
					segments = self.env['hr.segmentation'].search([('id','=',1)])
					segment_lines = []
					for segment in segments:
						#employees = self.env['hr.employee'].search([('department_id','=',department.id),('center_id','=',19),('segment_id','=',segment.id),('is_guard','=', False)])		
						employees = self.env['hr.employee'].search([('department_id','=',department.id),('segment_id','=',segment.id),('sub_segment_id','=',1),('is_guard','=', False)])		
						payslips = payslip_obj.sudo().search([('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','in',employees.ids)],order='employee_id')
						
						if payslips:
							for payslip in payslips:
								dept_wage = dept_wage + payslip.contract_id.wage
								line_ids = payslip_line_obj.search([('slip_id','=',payslip.id)])
								for line_id in line_ids:
									if line_id.code == 'NET':
										dept_net = line_id.total + dept_net
										net = line_id.total + net
									if line_id.code == 'BASIC':
										dept_basic = line_id.total + dept_basic
										basic = line_id.total + basic
									if line_id.code == 'GROSS':
										dept_gross = line_id.total + dept_gross
										gross = line_id.total + gross
									if line_id.code == 'MA':
										dept_mobile = line_id.total + dept_mobile
										mobile = line_id.total + mobile
									if line_id.code == 'FDA':
										dept_food = line_id.total + dept_food
										food = line_id.total + food
									if line_id.code == 'TRA':
										dept_trans = line_id.total + dept_trans
										trans = line_id.total + trans
									if line_id.code == 'FLA':
										dept_fuel = line_id.total + dept_fuel
										fuel = line_id.total + fuel
									if line_id.code == 'HRA':
										dept_housing = line_id.total + dept_housing
										housing = line_id.total + housing
									if line_id.code == 'SBIKA':
										dept_bike = line_id.total + dept_bike
										bike = line_id.total + bike
									if line_id.code == 'MEDA':
										dept_medical = line_id.total + dept_medical
										medical = line_id.total + medical
									if line_id.code == 'OSSA':
										dept_out_station = line_id.total + dept_out_station
										out_station = line_id.total + out_station
									if line_id.code == 'SSPA':
										dept_special_allw = line_id.total + dept_special_allw
										special_allw = line_id.total + special_allw														
												
									input_ids = payslip_input_obj.search([('payslip_id','=',payslip.id)])
									for input_id in input_ids:
										if input_id.code == 'ARS':
											dept_arrear = input_id.amount + dept_arrear
											arrear = input_id.amount + arrear
										if input_id.code == 'BNS':
											dept_bonus = input_id.amount + dept_bonus 
											bonus = input_id.amount + bonus 
										if input_id.code == 'INCTV':
											dept_incentive = input_id.amount + dept_incentive
											incentive = input_id.amount + incentive
										if input_id.code == 'OT':
											dept_over_time = input_id.amount + dept_over_time
											over_time = input_id.amount + over_time
										
											
										
							segment_line= ({
								'segment' : segment.name,
								'payslips' : payslips or False,
								})
								
							segment_lines.append(segment_line)		
					
					if len(segment_lines):
						recs.append({
							'department' : department.name,
							'segments' : segment_lines,
							'dept_net' : dept_net,
							'dept_basic' : dept_basic,
							'dept_gross' : dept_gross,
							'dept_arrear' : dept_arrear,
							'dept_bonus' : dept_bonus,
							'dept_mobile' : dept_mobile,
							'dept_food' : dept_food,
							'dept_trans' : dept_trans,
							'dept_incentive' : dept_incentive,
							'dept_over_time' : dept_over_time,
							'dept_housing' : dept_housing,
							'dept_wage' : dept_wage,
							'dept_fuel' : dept_fuel,
							'dept_bike' : dept_bike,
							'dept_medical' : dept_medical,
							'dept_out_station' : dept_out_station,
							'dept_special_allw' : dept_special_allw,
							})
	
		
		#IF Regioanl office
		if report_required == 'regional':
			centers = self.env['sos.center'].search([('id','!=',19)]) #19---> multan
			
			for center in centers:
				dept_net = 0
				dept_basic = 0
				dept_gross = 0
				dept_arrear = 0
				dept_bonus = 0
				dept_mobile = 0
				dept_food = 0
				dept_trans = 0
				dept_incentive = 0
				dept_over_time = 0
				dept_housing = 0
				dept_wage = 0
				dept_fuel = 0
				dept_bike = 0
				dept_medical = 0
				dept_out_station = 0
				dept_special_allw = 0
				
				if segment_wise == 'yes':
					segments = self.env['hr.segmentation'].search([('id','=', 1)])
					segment_lines = []
					for segment in segments:
						#employees = self.env['hr.employee'].search([('center_id','=',center.id),('is_guard','=', False),('department_id','!=',29),('segment_id','=',segment.id)])		
						employees = self.env['hr.employee'].search([('center_id','=',center.id),('is_guard','=', False),('department_id','!=',29),('segment_id','=',segment.id),('sub_segment_id','!=',1)])		
						payslips = payslip_obj.sudo().search([('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','in',employees.ids)],order='employee_id')

						if payslips:
							for payslip in payslips:
								dept_wage = dept_wage + payslip.contract_id.wage
								line_ids = payslip_line_obj.search([('slip_id','=',payslip.id)])
								for line_id in line_ids:
									if line_id.code == 'NET':
										dept_net = line_id.total + dept_net
										net = line_id.total + net
									if line_id.code == 'BASIC':
										dept_basic = line_id.total + dept_basic
										basic = line_id.total + basic
									if line_id.code == 'GROSS':
										dept_gross = line_id.total + dept_gross
										gross = line_id.total + gross
									if line_id.code == 'MA':
										dept_mobile = line_id.total + dept_mobile
										mobile = line_id.total + mobile
									if line_id.code == 'FDA':
										dept_food = line_id.total + dept_food
										food = line_id.total + food
									if line_id.code == 'TRA':
										dept_trans = line_id.total + dept_trans
										trans = line_id.total + trans
									if line_id.code == 'FLA':
										dept_fuel = line_id.total + dept_fuel
										fuel = line_id.total + fuel
									if line_id.code == 'HRA':
										dept_housing = line_id.total + dept_housing
										housing = line_id.total + housing
									if line_id.code == 'SBIKA':
										dept_bike = line_id.total + dept_bike
										bike = line_id.total + bike
						
									if line_id.code == 'MEDA':
										dept_medical = line_id.total + dept_medical
										medical = line_id.total + medical
							
									if line_id.code == 'OSSA':
										dept_out_station = line_id.total + dept_out_station
										out_station = line_id.total + out_station
							
									if line_id.code == 'SSPA':
										dept_special_allw = line_id.total + dept_special_allw
										special_allw = line_id.total + special_allw	
																				
									
									input_ids = payslip_input_obj.search([('payslip_id','=',payslip.id)])
									for input_id in input_ids:
										if input_id.code == 'ARS':
											dept_arrear = input_id.amount + dept_arrear
											arrear = input_id.amount + arrear
										if input_id.code == 'BNS':
											dept_bonus = input_id.amount + dept_bonus 
											bonus = input_id.amount + bonus 
										if input_id.code == 'INCTV':
											dept_incentive = input_id.amount + dept_incentive
											incentive = input_id.amount + incentive
										if input_id.code == 'OT':
											dept_over_time = input_id.amount + dept_over_time
											over_time = input_id.amount + over_time
							
							
							segment_line= ({
								'segment' : segment.name,
								'payslips' : payslips or False,
								})
								
							segment_lines.append(segment_line)
					
					if len(segment_lines):
						recs.append({
							'department' : center.name,
							'segments' : segment_lines,
							'dept_net' : dept_net,
							'dept_basic' : dept_basic,
							'dept_gross' : dept_gross,
							'dept_arrear' : dept_arrear,
							'dept_bonus' : dept_bonus,
							'dept_mobile' : dept_mobile,
							'dept_food' : dept_food,
							'dept_trans' : dept_trans,
							'dept_incentive' : dept_incentive,
							'dept_over_time' : dept_over_time,
							'dept_housing' : dept_housing,
							'dept_wage' : dept_wage,
							'dept_fuel' : dept_fuel,
							'dept_bike' : dept_bike,
							'dept_medical' : dept_medical,
							'dept_out_station' : dept_out_station,
							'dept_special_allw' : dept_special_allw,
							})		
							
		report = self.env['ir.actions.report']._get_report_from_name('sos.report_staff_gross_salarysheet')
		
		return  {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Payslip': recs,
			'Working_Days' : self.get_staff_working_days,
			'Lines' : self.get_staff_lines,
			'NET' : net,
			'GROSS' : gross,
			'ARREAR' : arrear,
			'BASIC' : basic,
			'MOBILE' : mobile,
			'FOOD' : food,
			'TRANS': trans,
			'BONUS' : bonus,
			'INCENTIVE' : incentive,
			'OVER_TIME' : over_time,
			'amount_in_word': self.amount_in_word,
			'HOUSING': housing,
			'WAGE': wage,
			'FUEL': fuel,
			'BIKE': bike,
			'MEDICAL': medical,
			'OUT_STATION' : out_station,
			'SPECIAL_ALLW' : special_allw,
			'get_date_formate' : self.get_date_formate,
		}
		
		

