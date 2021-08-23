import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models


class AirTravelSummaryReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_air_travel_summary'
	_description = 'Air Travel Summary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from'] or False
		date_to = data['form']['date_to'] and data['form']['date_to'] or False
		need_full_report = data['form']['need_full_report'] and data['form']['need_full_report'] or False
		
		recs = False
		total_amt = 0
		total_fare_amt = 0
		total_cancel_amt = 0
		
		if need_full_report:
			recs = self.env['sos.air.reservation'].search([],order='departure_date')
		
		if not need_full_report:
			recs = self.env['sos.air.reservation'].search([('booking_date','>=',date_from),('booking_date','<=',date_to)], order='departure_date')	
		
		if recs:
			for rec in recs:
				if rec.ticket_cancellation:
					total_cancel_amt += rec.cancellation_amt
					total_amt +=rec.cancellation_amt
					total_fare_amt += rec.fare
				else:
					total_fare_amt += rec.fare 
					total_amt +=rec.fare	
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_air_travel_summary')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'recs' : recs,
			'stat' : {'total':total_amt,'total_fare':total_fare_amt,'total_cancel':total_cancel_amt},		
			'get_date_formate' : self.get_date_formate,
		}