import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models


class RentCarSummaryReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_rent_car_summary'
	_description = 'Car Rent Summary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from'] or False
		date_to = data['form']['date_to'] and data['form']['date_to'] or False
		need_full_report = data['form']['need_full_report'] and data['form']['need_full_report'] or False
		
		if date_from and date_to:
			date_from = date_from + " 00:00:01"
			date_to = date_to + " 23:59:59"
		
		recs = False
		total_amt = 0
		total_fuel = 0
		total_rent = 0
		
		if need_full_report:
			recs = self.env['sos.car.approval'].search([],order='hiring_date')
		
		if not need_full_report:
			recs = self.env['sos.car.approval'].search([('hiring_date','>=',date_from),('hiring_date','<=',date_to)], order='hiring_date')
		
		if recs:
			for rec in recs:
				total_amt += rec.total_amount
				total_fuel += rec.fuel_amount
				total_rent += rec.total_rent 
			
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_rent_car_summary')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'recs' : recs,
			'stat' : {'total_amt':total_amt,'total_fuel':total_fuel,'total_rent':total_rent},		
			'get_date_formate' : self.get_date_formate,
		}