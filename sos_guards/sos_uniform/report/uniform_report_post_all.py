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



class ReportUniformPostAll(models.AbstractModel):
	_name = 'report.sos_uniform.report_uniformpostall'
	_description = 'All Post Uniform Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def _get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		state = data['form']['state'] and data['form']['state']
		center_id = data['form']['center_id'] and data['form']['center_id'][0]
		project_id = data['form']['project_id'] and data['form']['project_id'][0]
			
		posts = self.env['sos.post'].search([('project_id', '=', project_id), ('center_id', '=', center_id), ('active', '=', True)], order='name')
		res = []
		
		uniform_amount = 0
		shoe_amount = 0
		cap_amount = 0
		belt_amount = 0
		new_uniform_amount = 0
		new_shoe_amount = 0
		new_cap_amount = 0
		new_belt_amount = 0
		total_amount = 0
		
		for post in posts:
			dom = []
			dom = [('date', '>=', date_from), ('date', '<=', date_to)]
			dom += [('post_id', '=', post.id)]
			guards = self.env['hr.employee'].search_count([('current','=',True),('is_guard','=',True),('current_post_id','=',post.id)])
		
			if state in ['draft','open','review','approve','dispatch','done','reject','cancel']:
				dom += [('state', '=', state)]
			elif state == 'dispatch_deliver':
				dom += [('state', 'in', ['dispatch','done'])]	
			elif state == 'none_dispatched':
				dom += [('state', 'in', ['open','review','approve'])]
			elif state == 'all':
				dom += [('state', 'in', ['open','review','approve','dispatch','done','reject','cancel'])]	
			demands = self.env['sos.uniform.demand'].search(dom)
			
			uniform = 0
			shoe = 0
			cap = 0
			belt = 0
			new_uniform = 0
			new_shoe = 0
			new_cap = 0
			new_belt = 0
			total = 0
			
			for demand in demands:
				if demand.is_new_post:
					for d in demand.uniform_demand_line:
						if d.item_id.name == 'Uniform':
							new_uniform = new_uniform + (1 * d.qty)
						elif d.item_id.name == 'Cap':
							new_cap = new_cap + (1 * d.qty)
						elif d.item_id.name == 'Belt':
							new_belt = new_belt + (1 * d.qty)
						elif d.item_id.name == 'Shoe':
							new_shoe = new_shoe + (1 * d.qty)
						elif d.item_id.name == 'Uniform-Shoes':
							unew_niform = new_uniform + (1 * d.qty)
							shoe = shoe + (1 * d.qty)
						elif d.item_id.name == 'Uniform-Belt-Cap':
							new_cap = new_cap + (1 * d.qty)
							new_uniform = new_uniform + (1 * d.qty)
							new_belt = new_belt + (1 * d.qty)
						elif d.item_id.name == 'Belt-Cap':
							new_cap = new_cap + (1 * d.qty)
							new_belt = new_belt + (1 * d.qty)
						elif d.item_id.name == 'Shoe-Belt-Cap':
							new_cap = new_cap + (1 * d.qty)
							new_belt = new_belt + (1 * d.qty)	
							new_shoe = new_shoe + (1 * d.qty)

						elif d.item_id.name == 'New Deployment Kit':
							new_cap = new_cap + (1 * d.qty)
							new_belt = new_belt + (1 * d.qty)
							new_shoe = new_shoe + (1 * d.qty)
							new_uniform = new_uniform + (2 * d.qty)
						
						elif d.item_id.name == 'Complete Kit':
							cap = cap + (1 * d.qty)
							belt = belt + (1 * d.qty)
							shoe = shoe + (1 * d.qty)
							uniform = uniform + (1 * d.qty)	
				else:
					for d in demand.uniform_demand_line:
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
							
				total = uniform + shoe + belt + cap + new_uniform + new_shoe + new_belt + new_cap
			res.append({
				'post_name' : post.name,
				'uniform': uniform or '-',
				'shoe': shoe or '-',
				'cap': cap or '-',
				'belt': belt or '-',
				'new_uniform': new_uniform or '-',
				'new_shoe': new_shoe or '-',
				'new_belt': new_belt or '-',
				'new_cap': new_cap or '-',
				'total' : total or '-',
				'guards' : guards,
			})
			
			
			uniform_amount += uniform or 0
			shoe_amount += shoe or 0
			cap_amount += cap or 0
			belt_amount += belt or 0
			new_uniform_amount += new_uniform or 0
			new_shoe_amount += new_shoe or 0
			new_cap_amount += new_cap or 0
			new_belt_amount += new_belt or 0
			total_amount += total or 0
			
			
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_uniformpostall')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"Posts" : res or False,
			"Uniform" : uniform_amount,
			"Shoe" : shoe_amount,
			"Cap" : cap_amount,
			"Belt" : belt_amount,
			"New_Uniform" : new_uniform_amount,
			"New_Shoe" : new_shoe_amount,
			"New_Cap" : new_cap_amount,
			"New_Belt" : new_belt_amount,
			"Total" : total_amount,
			"get_date_formate" : self.get_date_formate,
		}
		
		
