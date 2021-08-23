import pdb
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

from odoo import netsvc
from odoo import models, fields, api 
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError

DAYOFWEEK_SELECTION = [
	('0', 'Sunday'),
	('1', 'Monday'),
	('2', 'Tuesday'),
	('3', 'Wednesday'),
	('4', 'Thursday'),
	('5', 'Friday'),
	('6', 'Saturday'),
]

def strToDate(strdate):
	return datetime.strptime(strdate, '%Y-%m-%d').date()

def strToDatetime(strdatetime):
	return datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
	
def dateToStr(ddate):
	return ddate.strftime('%Y-%m-%d')

def datetimeToStr(ddate):
	return ddate.strftime('%Y-%m-%d %H:%M:%S')

def utcDate(self, ddate):
	user = self.env.user
	local_tz = timezone(user.tz)
	local_date = local_tz.localize(ddate, is_dst=False)
	utc_date = local_date.astimezone(utc)
	return utc_date			

	
class hr_contract(models.Model):
	_name = 'hr.contract'
	_inherit = 'hr.contract'
	
	@api.depends('wage','transportation_allowance','house_rent_allowance','mobile_allowance','food_allowance','fuel_allowance', 
				'tds','voluntary_provident_fund','medical_insurance','supplementary_allowance','medical_allowance',
				'out_station_allowance','bike_maintenance_allowance','special_allowance','scholarship_allowance')
	@api.multi
	def _get_gross_salary(self):
		for rec in self:
			gross_salary = 0 
			gross_salary = (rec.wage + rec.transportation_allowance +  rec.house_rent_allowance + rec.mobile_allowance + rec.food_allowance + rec.fuel_allowance + rec.medical_allowance + rec.out_station_allowance + rec.bike_maintenance_allowance + rec.special_allowance + rec.scholarship_allowance + rec.supplementary_allowance  - rec.tds - rec.voluntary_provident_fund - rec.medical_insurance)
			rec.gross_salary = gross_salary
			
			
	@api.depends('wage','house_rent_allowance')
	@api.multi
	def _compute_gossi_deduction(self):
		for rec in self:
			if rec.employee_id.country_id.id == 194:
				rec.gossi_deduction = (rec.wage + rec.acomodation_allowance) * .1
			else:
				rec.gossi_deduction = 0
					
	mobile_allowance = fields.Integer("Mobile Allowance")
	fuel_allowance = fields.Integer("Fuel Allowance")
	food_allowance = fields.Integer("Food/Laundary Allowance")
	acomodation_allowance = fields.Integer("Rental Acomodation Allowance")
	md_house_allowance = fields.Integer("MD House Allowance")
	gossi_deduction = fields.Float('GOSI Deduction', compute='_compute_gossi_deduction')
	gross_salary = fields.Float(compute='_get_gross_salary', string="Gross Salary", store=False)
	medical_allowance = fields.Float('Medical Allowance')
	out_station_allowance = fields.Float('Out Station Allowance')
	bike_maintenance_allowance = fields.Float('Bike Maintenance Allowance')
	special_allowance = fields.Float('Special Allowance')
	scholarship_allowance = fields.Float('ScholarShip Allowance')
	
	
class hr_holidays(models.Model):
	_inherit = 'hr.leave'

	@api.multi
	def holidays_validate(self):
		res = super(hr_holidays, self).holidays_validate()
		unlink_ids = []

		for leave in self:
			if leave.type != 'remove':
				continue

			det_ids = self.env['hr.schedule.detail'].search([
				('schedule_id.employee_id', '=', leave.employee_id.id),('hour_from', '<=', leave.date_to),  ('hour_to', '>=', leave.date_from)],order='hour_from')
			for detail in det_ids:

				# Remove schedule details completely covered by leave
				if (leave.date_from <= detail.hour_from and leave.date_to >= detail.hour_to and detail.id not in unlink_ids):
					unlink_ids.append(detail)

				# Partial day on first day of leave
				elif detail.hour_from < leave.date_from <= detail.hour_to:
					dtLv = datetime.strptime(leave.date_from, OE_DTFORMAT)
					if leave.date_from == detail.hour_to:
						if detail.id not in unlink_ids.ids:
							unlink_ids.append(detail)
						else:
							dtEnd = dtLv + timedelta(seconds=-1)
							detail.write({'date_end': dtEnd.strftime(OE_DTFORMAT)})

				# Partial day on last day of leave
				elif detail.hour_to > leave.date_to >= detail.hour_from:
					dtLv = datetime.strptime(leave.date_to, OE_DTFORMAT)
					if leave.date_to != detail.hour_from:
						dtStart = dtLv + timedelta(seconds=+1)
						detail.write({'hour_from': dtStart.strftime(OE_DTFORMAT)})

		unlink_ids.unlink()
		return res
