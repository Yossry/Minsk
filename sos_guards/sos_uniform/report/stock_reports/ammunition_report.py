import pdb
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from pytz import timezone
import pytz, datetime
from dateutil import tz
from openerp import api, fields, models, _
from openerp.exceptions import UserError



class ReportAmmunition(models.AbstractModel):
	_name = 'report.sos_uniform.report_ammunition'
	_description = 'Ammunition Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def	get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		new_demands = False
		new_demand_list = []
		
		new_demand_30_bore_total = 0
		new_demand_12_bore_total = 0
		new_demand_7mm_total = 0
		new_demand_8mm_total = 0
		new_demand_44mm_total = 0
		new_demand_9mm_total = 0
		new_demand_222_total = 0
		new_demand_mouzer_total = 0
		
			
		#***** New Deployments *****#
		new_demands = self.env['sos.weapon.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','new_deployment')])
		
		if new_demands:
			new_demand_list = []
			for demand in new_demands: 
				dispatch_lines = demand.weapon_dispatch_line.filtered(lambda x: x.product_id.id in (13,265,15,16,17,77,105))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'New Deployment',
							'demand_no' : demand.name,
							'30_bore' : line.product_qty if line.product_id.id == 13 else '',
							'12_bore' : line.product_qty if line.product_id.id == 265 else '',
							'7mm' : line.product_qty if line.product_id.id == 15 else '',
							'8mm' : line.product_qty if line.product_id.id == 16 else '',
							'44mm' : line.product_qty if line.product_id.id == 17 else '',
							'9mm' : line.product_qty if line.product_id.id == 17 else '',
							'222' : line.product_qty if line.product_id.id == 105 else '',
							'mouzer' : '',
						})
						new_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 13:
							new_demand_30_bore_total = new_demand_30_bore_total + line.product_qty
						if line.product_id.id == 265:
							new_demand_12_bore_total = new_demand_12_bore_total + line.product_qty
						if line.product_id.id == 15:
							new_demand_7mm_total = new_demand_7mm_total + line.product_qty
						if line.product_id.id == 16:
							new_demand_8mm_total = new_demand_8mm_total + line.product_qty
						if line.product_id.id == 17:
							new_demand_44mm_total = new_demand_44mm_total + line.product_qty
						if line.product_id.id == 77:
							new_demand_9mm_total = new_demand_9mm_total + line.product_qty
						if line.product_id.id == 105:
							new_demand_222_total = new_demand_222_total + line.product_qty
						#if line.product_id.id == 333:
						new_demand_mouzer_total = 0
						
		
		#***** Complain *****#					
		complain_demands = False
		complain_demand_list = []
		
		complain_demand_30_bore_total = 0
		complain_demand_12_bore_total = 0
		complain_demand_7mm_total = 0
		complain_demand_8mm_total = 0
		complain_demand_44mm_total = 0
		complain_demand_9mm_total = 0
		complain_demand_222_total = 0
		complain_demand_mouzer_total = 0
		
			
		complain_demands = self.env['sos.weapon.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','complain')])
		
		if complain_demands:
			complain_demand_list = []
			for demand in complain_demands:  
				dispatch_lines = demand.weapon_dispatch_line.filtered(lambda x: x.product_id.id in (13,265,15,16,17,77,105))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Complain',
							'demand_no' : demand.name,
							'30_bore' : line.product_qty if line.product_id.id == 13 else '',
							'12_bore' : line.product_qty if line.product_id.id == 265 else '',
							'7mm' : line.product_qty if line.product_id.id == 15 else '',
							'8mm' : line.product_qty if line.product_id.id == 16 else '',
							'44mm' : line.product_qty if line.product_id.id == 17 else '',
							'9mm' : line.product_qty if line.product_id.id == 77 else '',
							'222' : line.product_qty if line.product_id.id == 105 else '',
							'mouzer' : '',
						})
						complain_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 13:
							complain_demand_30_bore_total = complain_demand_30_bore_total + line.product_qty
						if line.product_id.id == 265:
							complain_demand_12_bore_total = complain_demand_12_bore_total + line.product_qty
						if line.product_id.id == 15:
							complain_demand_7mm_total = complain_demand_7mm_total + line.product_qty
						if line.product_id.id == 16:
							complain_demand_8mm_total = complain_demand_8mm_total + line.product_qty
						if line.product_id.id == 17:
							complain_demand_44mm_total = complain_demand_44mm_total + line.product_qty
						if line.product_id.id == 77:
							complain_demand_9mm_total = complain_demand_9mm_total + line.product_qty
						if line.product_id.id == 105:
							complain_demand_222_total = complain_demand_222_total + line.product_qty
						#if line.product_id.id == 333:
						complain_demand_mouzer_total = 0
						
		#***** Additional Guards *****#				
		add_guard_demands = False
		add_guard_demand_list = []
		
		add_guard_demand_30_bore_total = 0
		add_guard_demand_12_bore_total = 0
		add_guard_demand_7mm_total = 0
		add_guard_demand_8mm_total = 0
		add_guard_demand_44mm_total = 0
		add_guard_demand_9mm_total = 0
		add_guard_demand_222_total = 0
		add_guard_demand_mouzer_total = 0
		
			
		add_guard_demands = self.env['sos.weapon.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','additional_guard')])
		
		if add_guard_demands:
			add_guard_demand_list = []
			for demand in add_guard_demands:  
				dispatch_lines = demand.weapon_dispatch_line.filtered(lambda x: x.product_id.id in (13,265,15,16,17,77,105))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Additional Guards',
							'demand_no' : demand.name,
							'30_bore' : line.product_qty if line.product_id.id == 13 else '',
							'12_bore' : line.product_qty if line.product_id.id == 265 else '',
							'7mm' : line.product_qty if line.product_id.id == 15 else '',
							'8mm' : line.product_qty if line.product_id.id == 16 else '',
							'44mm' : line.product_qty if line.product_id.id == 17 else '',
							'9mm' : line.product_qty if line.product_id.id == 77 else '',
							'222' : line.product_qty if line.product_id.id == 105 else '',
							'mouzer' : '',
						})
						add_guard_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 13:
							add_guard_demand_30_bore_total = add_guard_demand_30_bore_total + line.product_qty
						if line.product_id.id == 265:
							add_guard_demand_12_bore_total = add_guard_demand_12_bore_total + line.product_qty
						if line.product_id.id == 15:
							add_guard_demand_7mm_total = add_guard_demand_7mm_total + line.product_qty
						if line.product_id.id == 16:
							add_guard_demand_8mm_total = add_guard_demand_8mm_total + line.product_qty
						if line.product_id.id == 17:
							add_guard_demand_44mm_total = add_guard_demand_44mm_total + line.product_qty
						if line.product_id.id == 77:
							add_guard_demand_9mm_total = add_guard_demand_9mm_total + line.product_qty
						if line.product_id.id == 105:
							add_guard_demand_222_total = add_guard_demand_222_total + line.product_qty
						#if line.product_id.id == 333:
						add_guard_demand_mouzer_total = 0
						
		
		#***** Replacement *****#				
		replacement_demands = False
		replacement_demand_list = []
		
		replacement_demand_30_bore_total = 0
		replacement_demand_12_bore_total = 0
		replacement_demand_7mm_total = 0
		replacement_demand_8mm_total = 0
		replacement_demand_44mm_total = 0
		replacement_demand_9mm_total = 0
		replacement_demand_222_total = 0
		replacement_demand_mouzer_total = 0
		
			
		replacement_demands = self.env['sos.weapon.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','replacement')])
		
		if replacement_demands:
			replacement_demand_list = []
			for demand in replacement_demands:
				dispatch_lines = demand.weapon_dispatch_line.filtered(lambda x: x.product_id.id in (13,265,15,16,17,77,105))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Replacement',
							'demand_no' : demand.name,
							'30_bore' : line.product_qty if line.product_id.id == 13 else '',
							'12_bore' : line.product_qty if line.product_id.id == 265 else '',
							'7mm' : line.product_qty if line.product_id.id == 15 else '',
							'8mm' : line.product_qty if line.product_id.id == 16 else '',
							'44mm' : line.product_qty if line.product_id.id == 17 else '',
							'9mm' : line.product_qty if line.product_id.id == 77 else '',
							'222' : line.product_qty if line.product_id.id == 105 else '',
							'mouzer' : '',
						})
						replacement_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 13:
							replacement_demand_30_bore_total = replacement_demand_30_bore_total + line.product_qty
						if line.product_id.id == 265:
							replacement_demand_12_bore_total = replacement_demand_12_bore_total + line.product_qty
						if line.product_id.id == 15:
							replacement_demand_7mm_total = replacement_demand_7mm_total + line.product_qty
						if line.product_id.id == 16:
							replacement_demand_8mm_total = replacement_demand_8mm_total + line.product_qty
						if line.product_id.id == 17:
							replacement_demand_44mm_total = replacement_demand_44mm_total + line.product_qty
						if line.product_id.id == 77:
							replacement_demand_9mm_total = replacement_demand_9mm_total + line.product_qty
						if line.product_id.id == 105:
							replacement_demand_222_total = replacement_demand_222_total + line.product_qty
						#if line.product_id.id == 333:
						replacement_demand_mouzer_total = 0								
						
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_ammunition')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			"New_Demands" : new_demand_list,
			"New_Demand_Total": {'total_30_bore': new_demand_30_bore_total, 'total_12_bore' : new_demand_12_bore_total, 'total_7mm' : new_demand_7mm_total, 'total_8mm' : new_demand_8mm_total,'total_44mm' : new_demand_44mm_total,'total_9mm' : new_demand_9mm_total,'total_222' : new_demand_222_total,'total_mouzer' : new_demand_mouzer_total},
			"Complain_Demands" : complain_demand_list,
			"Complain_Demand_Total": {'total_30_bore': complain_demand_30_bore_total, 'total_12_bore' :complain_demand_12_bore_total, 'total_7mm' : complain_demand_7mm_total, 'total_8mm' : complain_demand_8mm_total,'total_44mm' : complain_demand_44mm_total,'total_9mm' : complain_demand_9mm_total,'total_222' : complain_demand_222_total,'total_mouzer' : complain_demand_mouzer_total},
			'Add_Guard_Demands' : add_guard_demand_list,
			"Add_Guard_Demand_Total": {'total_30_bore': add_guard_demand_30_bore_total, 'total_12_bore' :add_guard_demand_12_bore_total, 'total_7mm' : add_guard_demand_7mm_total, 'total_8mm' : add_guard_demand_8mm_total,'total_44mm' : add_guard_demand_44mm_total,'total_9mm' : add_guard_demand_9mm_total,'total_222' : add_guard_demand_222_total,'total_mouzer' : add_guard_demand_mouzer_total},
			'Replacement_Demands' : replacement_demand_list,
			"Replacement_Demand_Total": {'total_30_bore': replacement_demand_30_bore_total, 'total_12_bore' :replacement_demand_12_bore_total, 'total_7mm' : replacement_demand_7mm_total, 'total_8mm' : replacement_demand_8mm_total,'total_44mm' : replacement_demand_44mm_total,'total_9mm' : replacement_demand_9mm_total,'total_222' : replacement_demand_222_total,'total_mouzer' : replacement_demand_mouzer_total},
			"get_date_formate" : self.get_date_formate,
		}
		
		
