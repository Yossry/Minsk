import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models
from odoo.tools.amount_to_text_en import amount_to_text
from odoo.tools.amount_to_text_en import english_number


class ReportStaffSalarySheet(models.AbstractModel):
	_name = 'report.sos.report_staffsalarysheet'
	_description = 'Staff Salary Sheet Report'

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

		payslip_obj = self.env['hr.payslip']
		payslip_line_obj = self.env['hr.payslip.line']
		payslip_input_obj = self.env['hr.payslip.input']
				
		payslip_ids = payslip_obj.sudo().search([('date_from','>=',date_from),('date_to','<=',date_to)],order='')
		
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
		fine =0
		other_deduction = 0
		gossi = 0
		housing = 0
		wage = 0
		fuel = 0
		

		for payslip_id in payslip_ids:

			wage = wage + payslip_id.contract_id.wage

			line_ids = payslip_line_obj.search([('slip_id','=',payslip_id.id)])
			for line_id in line_ids:
				if line_id.code == 'NET':
					net = line_id.total + net
				if line_id.code == 'BASIC':
					basic = line_id.total + basic
				if line_id.code == 'GROSS':
					gross = line_id.total + gross
				if line_id.code == 'MA':
					mobile = line_id.total + mobile
				if line_id.code == 'FDA':
					food = line_id.total + food
				if line_id.code == 'TRA':
					trans = line_id.total + trans
				if line_id.code == 'FLA':
					fuel = line_id.total + fuel
				if line_id.code == 'GD':
					gossi = line_id.total + gossi
				if line_id.code == 'HRA':
					housing = line_id.total + housing
				
			input_ids = payslip_input_obj.search([('payslip_id','=',payslip_id.id)])
			for input_id in input_ids:
				if input_id.code == 'ARS':
					arrear = input_id.amount + arrear
				if input_id.code == 'BNS':
					bonus = input_id.amount + bonus 
				if input_id.code == 'INCTV':
					incentive = input_id.amount + incentive
				if input_id.code == 'OT':
					over_time = input_id.amount + over_time
				if input_id.code == 'ADV':
					advance = input_id.amount + advance
				if input_id.code == 'FINE':
					fine = input_id.amount + fine
				if input_id.code == 'ODE':
					other_deduction = input_id.amount + other_deduction

		report = self.env['ir.actions.report']._get_report_from_name('sos.report_staffsalarysheet')
		
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'Payslip': payslip_ids,
			'Working_Days' : self.get_staff_working_days,
			'Lines' : self.get_staff_lines,
			'NET' : net,
			'GROSS' : gross,
			'BASIC' : basic,
			'ARREAR' : arrear,
			'MOBILE' : mobile,
			'FOOD' : food,
			'TRANS': trans,
			'BONUS' : bonus,
			'INCENTIVE' : incentive,
			'OVER_TIME' : over_time,
			'ADVANCE' : advance,
			'FINE' : fine,
			'GOSSI' : gossi,
			'OTHER_DEDUCTION' : other_deduction,
			'get_date_formate' : self.get_date_formate,
			'amount_in_word': self.amount_in_word,
			'HOUSING': housing,
			'WAGE': wage,
			'FUEL': fuel,
		}