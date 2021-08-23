import pdb
import time
from datetime import datetime, timedelta
from pytz import timezone
from odoo import api, models


class GuestHouseSummaryReport(models.AbstractModel):
	_name = 'report.sos_complaint.report_guest_house_summary'
	_description = 'Guest House Summary Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
	
	@api.model
	def _get_report_values(self, docids, data=None):
		check_in = data['form']['check_in'] and data['form']['check_in'] or False
		check_out = data['form']['check_out'] and data['form']['check_out'] or False
		need_full_report = data['form']['need_full_report'] and data['form']['need_full_report'] or False
		
		if check_in and check_out:
			check_in = check_in + " 00:00:01"
			check_out = check_out + " 23:59:59"
		
		recs = False
		total_amt = 0
		total_food = 0
		total_rent = 0
		
		if need_full_report:
			recs = self.env['sos.guest.house.approval'].search([],order='check_in')
		
		if not need_full_report:
			recs = self.env['sos.guest.house.approval'].search([('check_in','>=',check_in),('check_out','<=',check_out)], order='check_in')
		
		if recs:
			for rec in recs:
				total_amt += rec.total_amount
				total_food += rec.food_amount
				total_rent += rec.total_rent 
			
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_complaint.report_guest_house_summary')
		return {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'data': data['form'],
			'docs': self,
			'time': time,
			'recs' : recs,
			'stat' : {'total_amt':total_amt,'total_food':total_food,'total_rent':total_rent},		
			'get_date_formate' : self.get_date_formate,
		}