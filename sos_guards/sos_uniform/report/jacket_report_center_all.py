import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportJacketCenterAll(models.AbstractModel):
	_name = 'report.sos_uniform.report_jacketcenterall'
	_description = 'All Centers Jacket Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		centers = self.env['sos.center'].search([], order='name')
		res = []
		
		total_jacket = 0
		total_jersey = 0
		total_rain_coat = 0
		total_new_jacket = 0
		total_new_jersey = 0
		total_new_rain_coat = 0
		grand_total = 0
		
		for center in centers:
			dom = []
			dom = [('date', '>=', date_from), ('date', '<=', date_to)]
			dom += [('center_id', '=', center.id)]
			guards = self.env['hr.employee'].search_count([('current','=',True),('is_guard','=',True),('center_id','=',center.id)])	
			demands = self.env['sos.jacket.demand'].search(dom)
			
			jacket = 0
			jersey = 0
			rain_coat = 0
			new_jacket = 0
			new_jersey = 0
			new_rain_coat = 0
			total = 0
			
			for demand in demands:
				if demand.new_posts:
					for d in demand.jacket_demand_line:
						if d.item == 'jersey':
							new_jersey = new_jersey + (1 * d.qty)
						elif d.item == 'jacket':
							new_jacket = new_jacket + (1 * d.qty)
						elif d.item == 'raincoat':
							new_rain_coat = new_rain_coat + (1 * d.qty)
				else:
					for d in demand.jacket_demand_line:
						if d.item == 'jersey':
							jersey = jersey + (1 * d.qty)
						elif d.item == 'jacket':
							jacket = jacket + (1 * d.qty)
						elif d.item == 'raincoat':
							rain_coat =rain_coat + (1 * d.qty)
							
							
			total = jersey + jacket + rain_coat + new_jersey + new_jacket + new_rain_coat				
							
							
			res.append({
				'center_name' : center.name,
				'jacket': jacket or '-',
				'jersey': jersey or '-',
				'rain_coat': rain_coat or '-',
				'new_jacket': new_jacket or '-',
				'new_jersey': new_jersey or '-',
				'new_rain_coat': new_rain_coat or '-',
				'total' : total or '-',
				'guards' : guards,
				})		
			
			total_jacket += jacket
			total_jersey += jersey
			total_rain_coat += rain_coat
			total_new_jacket += new_jacket
			total_new_jersey += new_jersey
			total_new_rain_coat += new_rain_coat 
			grand_total += total
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_jacketcenterall')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"Jacket" : total_jacket or '-',
			"Jersey" : total_jersey or '-',
			"Rain_Coat" : total_rain_coat or '-',
			"New_Jacket" : total_new_jacket or '-',
			"New_Jersey" : total_new_jersey or '-',
			"New_Rain_Coat" : total_new_rain_coat or '-',
			"Total" : grand_total or '-',
			"get_date_formate" : self.get_date_formate,
		}
		
		
		
