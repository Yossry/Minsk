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



class ReportSateftUsage(models.AbstractModel):
	_name = 'report.sos_uniform.report_safetyusage'
	_description = 'Safety Stock Usage'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		centers = self.env['sos.center'].search([], order='name')
		
		res = []
		total_uniform = 0
		total_shoe = 0
		total_cap = 0
		total_belt = 0
		grand_total = 0
		
		for center in centers:
			demands = self.env['sos.uniform.demand'].search([('center_id', '=', center.id),('demand_type', '=', 'safety'),('date', '>=', date_from), ('date', '<=', date_to)])
			guards = self.env['hr.employee'].search_count([('current','=',True),('is_guard','=',True),('center_id','=',center.id)])
			
			uniform = 0
			shoe = 0
			cap = 0
			belt = 0
			total = 0
			
			for demand in demands:
				for d in demand.uniform_demand_line:
					if d.action == 'safety':
						if d.item_id.name == 'Uniform':
							uniform = uniform + (1 * d.qty)
						elif d.item_id.name == 'Cap':
							cap = cap + (1 * d.qty)
						elif d.item_id.name == 'Belt':
							belt = belt + (1 * d.qty)
						elif d.item_id.name == 'Shoe':
							shoe = shoe + (1 * d.qty)
						elif d.item_id.name == 'Uniform-Shoes':
							uniform = uniform + (1 * d.qty)
							shoe = shoe + (1 * d.qty)
						elif d.item_id.name == 'Uniform-Belt-Cap':
							cap = cap + (1 * d.qty)
							uniform = uniform + (1 * d.qty)
							belt = belt + (1 * d.qty)
						elif d.item_id.name == 'Belt-Cap':
							cap = cap + (1 * d.qty)
							belt = belt + (1 * d.qty)
						elif d.item_id.name == 'Shoe-Belt-Cap':
							cap = cap + (1 * d.qty)
							belt = belt + (1 * d.qty)	
							shoe = shoe + (1 * d.qty)

						elif d.item_id.name == 'New Deployment Kit':
							cap = cap + (1 * d.qty)
							belt = belt + (1 * d.qty)
							shoe = shoe + (1 * d.qty)
							uniform = uniform + (2 * d.qty)
						elif d.item_id.name == 'Complete Kit':
							cap = cap + (1 * d.qty)
							belt = belt + (1 * d.qty)
							shoe = shoe + (1 * d.qty)
							uniform = uniform + (1 * d.qty)	
							
				total = uniform + shoe + belt + cap
			res.append({
				'center_name' : center.name,
				'uniform': uniform or '-',
				'shoe': shoe or '-',
				'cap': cap or '-',
				'belt': belt or '-',
				'total' : total or '-',
				'guards' : guards,
			})
			
			
			total_uniform += uniform or 0
			total_shoe += shoe or 0
			total_cap += cap or 0
			total_belt += belt or 0
			grand_total += total or 0
			
			
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_safetyusage')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Centers" : res or False,
			"Uniform" : total_uniform,
			"Shoe" : total_shoe,
			"Cap" : total_cap,
			"Belt" : total_belt,
			"Total" : grand_total,
			"get_date_formate" : self.get_date_formate,
		}
		
		
