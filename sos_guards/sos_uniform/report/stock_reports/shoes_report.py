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



class ReportShoes(models.AbstractModel):
	_name = 'report.sos_uniform.report_shoes'
	_description = 'SOS Shoes Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		new_demands = False
		new_demand_list = []
		
		new_demand_7_total = 0
		new_demand_8_total = 0
		new_demand_9_total = 0
		new_demand_10_total = 0
		new_demand_11_total = 0
		new_demand_12_total = 0
		
		#***** New Deployments *****#
		new_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','new_deployment')])
		
		if new_demands:
			new_demand_list = []
			for demand in new_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (246,247,248,249,250,251))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'New Deployment',
							'demand_no' : demand.name,
							'7' : line.product_qty if line.product_id.id == 246 else '',
							'8' : line.product_qty if line.product_id.id == 247 else '',
							'9' : line.product_qty if line.product_id.id == 248 else '',
							'10' : line.product_qty if line.product_id.id == 249 else '',
							'11' : line.product_qty if line.product_id.id == 250 else '',
							'12' : line.product_qty if line.product_id.id == 251 else '',
						})
						
						new_demand_list.append(res)						
						
						##Totals
						if line.product_id.id == 246:
							new_demand_7_total = new_demand_7_total + line.product_qty
						if line.product_id.id == 247:
							new_demand_8_total = new_demand_8_total + line.product_qty
						if line.product_id.id == 248:
							new_demand_9_total = new_demand_9_total + line.product_qty
						if line.product_id.id == 249:
							new_demand_10_total = new_demand_10_total + line.product_qty
						if line.product_id.id == 250:
							new_demand_11_total = new_demand_11_total + line.product_qty
						if line.product_id.id == 251:
							new_demand_12_total = new_demand_12_total + line.product_qty
		
		#***** Complaints *****#
		complain_demands = False
		complain_demand_list = []
		
		complain_demand_7_total = 0
		complain_demand_8_total = 0
		complain_demand_9_total = 0
		complain_demand_10_total = 0
		complain_demand_11_total = 0
		complain_demand_12_total = 0
		
		complain_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','complain')])
		
		if complain_demands:
			complain_demand_list = []
			for demand in complain_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (246,247,248,249,250,251))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Complain',
							'demand_no' : demand.name,
							'7' : line.product_qty if line.product_id.id == 246 else '',
							'8' : line.product_qty if line.product_id.id == 247 else '',
							'9' : line.product_qty if line.product_id.id == 248 else '',
							'10' : line.product_qty if line.product_id.id == 249 else '',
							'11' : line.product_qty if line.product_id.id == 250 else '',
							'12' : line.product_qty if line.product_id.id == 251 else '',
						})
						
						complain_demand_list.append(res)						
						
						##Totals
						if line.product_id.id == 246:
							complain_demand_7_total = complain_demand_7_total + line.product_qty
						if line.product_id.id == 247:
							complain_demand_8_total = complain_demand_8_total + line.product_qty
						if line.product_id.id == 248:
							complain_demand_9_total = complain_demand_9_total + line.product_qty
						if line.product_id.id == 249:
							complain_demand_10_total = complain_demand_10_total + line.product_qty
						if line.product_id.id == 250:
							complain_demand_11_total = complain_demand_11_total + line.product_qty
						if line.product_id.id == 251:
							complain_demand_12_total = complain_demand_12_total + line.product_qty
							
		#***** Additional Guard *****#
		add_guard_demands = False
		add_guard_demand_list = []
		
		add_guard_demand_7_total = 0
		add_guard_demand_8_total = 0
		add_guard_demand_9_total = 0
		add_guard_demand_10_total = 0
		add_guard_demand_11_total = 0
		add_guard_demand_12_total = 0
		
		add_guard_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','additional_guard')])
		
		if add_guard_demands:
			add_guard_demand_list = []
			for demand in add_guard_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (246,247,248,249,250,251))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Additional Guard',
							'demand_no' : demand.name,
							'7' : line.product_qty if line.product_id.id == 246 else '',
							'8' : line.product_qty if line.product_id.id == 247 else '',
							'9' : line.product_qty if line.product_id.id == 248 else '',
							'10' : line.product_qty if line.product_id.id == 249 else '',
							'11' : line.product_qty if line.product_id.id == 250 else '',
							'12' : line.product_qty if line.product_id.id == 251 else '',
						})
						
						add_guard_demand_list.append(res)						
						
						##Totals
						if line.product_id.id == 246:
							add_guard_demand_7_total = add_guard_demand_7_total + line.product_qty
						if line.product_id.id == 247:
							add_guard_demand_8_total = add_guard_demand_8_total + line.product_qty
						if line.product_id.id == 248:
							add_guard_demand_9_total = add_guard_demand_9_total + line.product_qty
						if line.product_id.id == 249:
							add_guard_demand_10_total = add_guard_demand_10_total + line.product_qty
						if line.product_id.id == 250:
							add_guard_demand_11_total = add_guard_demand_11_total + line.product_qty
						if line.product_id.id == 251:
							add_guard_demand_12_total = add_guard_demand_12_total + line.product_qty
		
		
		#***** Replacement *****#
		replacement_demands = False
		replacement_demand_list = []
		
		replacement_demand_7_total = 0
		replacement_demand_8_total = 0
		replacement_demand_9_total = 0
		replacement_demand_10_total = 0
		replacement_demand_11_total = 0
		replacement_demand_12_total = 0
		
		replacement_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','replacement')])
		
		if replacement_demands:
			replacement_demand_list = []
			for demand in replacement_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (246,247,248,249,250,251))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Replacement',
							'demand_no' : demand.name,
							'7' : line.product_qty if line.product_id.id == 246 else '',
							'8' : line.product_qty if line.product_id.id == 247 else '',
							'9' : line.product_qty if line.product_id.id == 248 else '',
							'10' : line.product_qty if line.product_id.id == 249 else '',
							'11' : line.product_qty if line.product_id.id == 250 else '',
							'12' : line.product_qty if line.product_id.id == 251 else '',
						})
						
						replacement_demand_list.append(res)						
						
						##Totals
						if line.product_id.id == 246:
							replacement_demand_7_total = replacement_demand_7_total + line.product_qty
						if line.product_id.id == 247:
							replacement_demand_8_total = replacement_demand_8_total + line.product_qty
						if line.product_id.id == 248:
							replacement_demand_9_total = replacement_demand_9_total + line.product_qty
						if line.product_id.id == 249:
							replacement_demand_10_total = replacement_demand_10_total + line.product_qty
						if line.product_id.id == 250:
							replacement_demand_11_total = replacement_demand_11_total + line.product_qty
						if line.product_id.id == 251:
							replacement_demand_12_total = replacement_demand_12_total + line.product_qty																
					
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_shoes')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"New_Demands" : new_demand_list,
			"New_Demand_Total": {'total_7': new_demand_7_total, 'total_8' : new_demand_8_total, 'total_9' : new_demand_9_total, 'total_10' : new_demand_10_total, 'total_11' : new_demand_11_total,'total_12' : new_demand_12_total},
			"Complain_Demands" : complain_demand_list,
			"Complain_Demand_Total": {'total_7': complain_demand_7_total, 'total_8' : complain_demand_8_total, 'total_9' : complain_demand_9_total, 'total_10' : complain_demand_10_total, 'total_11' : complain_demand_11_total,'total_12' : complain_demand_12_total},
			"Add_Guard_Demands" : add_guard_demand_list,
			"Add_Guard_Demand_Total": {'total_7': add_guard_demand_7_total, 'total_8' : add_guard_demand_8_total, 'total_9' : add_guard_demand_9_total, 'total_10' : add_guard_demand_10_total, 'total_11' : add_guard_demand_11_total,'total_12' : add_guard_demand_12_total},
			"Replacement_Demands" : replacement_demand_list,
			"Replacement_Demand_Total": {'total_7': replacement_demand_7_total, 'total_8' : replacement_demand_8_total, 'total_9' : replacement_demand_9_total, 'total_10' : replacement_demand_10_total, 'total_11' : replacement_demand_11_total,'total_12' : replacement_demand_12_total},
			"get_date_formate" : self.get_date_formate,
		}
		
		
