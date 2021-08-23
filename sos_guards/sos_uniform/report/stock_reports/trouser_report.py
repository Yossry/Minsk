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



class ReportTrouser(models.AbstractModel):
	_name = 'report.sos_uniform.report_trouser'
	_description = 'SOS Trouser Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def get_report_values(self, docids, data=None):
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		new_demands = False
		
		new_demand_list = []
		new_demand_32_total = 0
		new_demand_34_total = 0
		new_demand_36_total = 0
		new_demand_38_total = 0
		new_demand_40_total = 0
		new_demand_42_total = 0
		new_demand_44_total = 0
		
		#***** New Deployments *****#
		new_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','new_deployment')])
		
		if new_demands:
			new_demand_list = []
			for demand in new_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (270, 271, 272, 273, 274, 275, 276))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'New Deployment',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 270 else '',
							'34' : line.product_qty if line.product_id.id == 271 else '',
							'36' : line.product_qty if line.product_id.id == 272 else '',
							'38' : line.product_qty if line.product_id.id == 273 else '',
							'40' : line.product_qty if line.product_id.id == 274 else '',
							'42' : line.product_qty if line.product_id.id == 275 else '',
							'44' : line.product_qty if line.product_id.id == 276 else '',
						})
						new_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 270:
							new_demand_32_total = new_demand_32_total + line.product_qty
						if line.product_id.id == 271:
							new_demand_34_total = new_demand_34_total + line.product_qty
						if line.product_id.id == 272:
							new_demand_36_total = new_demand_36_total + line.product_qty
						if line.product_id.id == 273:
							new_demand_38_total = new_demand_38_total + line.product_qty
						if line.product_id.id == 274:
							new_demand_40_total = new_demand_40_total + line.product_qty
						if line.product_id.id == 275:
							new_demand_42_total = new_demand_42_total + line.product_qty
						if line.product_id.id == 276:
							new_demand_44_total = new_demand_44_total + line.product_qty
							
		
		
		#***** Complaints *****#
		complain_demands = False
		
		complain_demand_list = []
		complain_demand_32_total = 0
		complain_demand_34_total = 0
		complain_demand_36_total = 0
		complain_demand_38_total = 0
		complain_demand_40_total = 0
		complain_demand_42_total = 0
		complain_demand_44_total = 0
		
		complain_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','complain')])
		
		if complain_demands:
			complain_demand_list = []
			for demand in complain_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (270, 271, 272, 273, 274, 275, 276))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Complain',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 270 else '',
							'34' : line.product_qty if line.product_id.id == 271 else '',
							'36' : line.product_qty if line.product_id.id == 272 else '',
							'38' : line.product_qty if line.product_id.id == 273 else '',
							'40' : line.product_qty if line.product_id.id == 274 else '',
							'42' : line.product_qty if line.product_id.id == 275 else '',
							'44' : line.product_qty if line.product_id.id == 276 else '',
						})
						complain_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 270:
							complain_demand_32_total = complain_demand_32_total + line.product_qty
						if line.product_id.id == 271:
							complain_demand_34_total = complain_demand_34_total + line.product_qty
						if line.product_id.id == 272:
							complain_demand_36_total =complain_demand_36_total + line.product_qty
						if line.product_id.id == 273:
							complain_demand_38_total = complain_demand_38_total + line.product_qty
						if line.product_id.id == 274:
							complain_demand_40_total = complain_demand_40_total + line.product_qty
						if line.product_id.id == 275:
							complain_demand_42_total = complain_demand_42_total + line.product_qty
						if line.product_id.id == 276:
							complain_demand_44_total = complain_demand_44_total + line.product_qty					
		
		
		#*****  Additional Guards *****#
		add_guard_demands = False
		
		add_guard_demand_list = []
		add_guard_demand_32_total = 0
		add_guard_demand_34_total = 0
		add_guard_demand_36_total = 0
		add_guard_demand_38_total = 0
		add_guard_demand_40_total = 0
		add_guard_demand_42_total = 0
		add_guard_demand_44_total = 0
		
		add_guard_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','additional_guard')])
		
		if add_guard_demands:
			add_guard_demand_list = []
			for demand in add_guard_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (270, 271, 272, 273, 274, 275, 276))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Additional Guard',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 270 else '',
							'34' : line.product_qty if line.product_id.id == 271 else '',
							'36' : line.product_qty if line.product_id.id == 272 else '',
							'38' : line.product_qty if line.product_id.id == 273 else '',
							'40' : line.product_qty if line.product_id.id == 274 else '',
							'42' : line.product_qty if line.product_id.id == 275 else '',
							'44' : line.product_qty if line.product_id.id == 276 else '',
						})
						add_guard_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 270:
							add_guard_demand_32_total = add_guard_demand_32_total + line.product_qty
						if line.product_id.id == 271:
							add_guard_demand_34_total = add_guard_demand_34_total + line.product_qty
						if line.product_id.id == 272:
							add_guard_demand_36_total = add_guard_demand_36_total + line.product_qty
						if line.product_id.id == 273:
							add_guard_demand_38_total = add_guard_demand_38_total + line.product_qty
						if line.product_id.id == 274:
							add_guard_demand_40_total = add_guard_demand_40_total + line.product_qty
						if line.product_id.id == 275:
							add_guard_demand_42_total = add_guard_demand_42_total + line.product_qty
						if line.product_id.id == 276:
							add_guard_demand_44_total = add_guard_demand_44_total + line.product_qty
							
												
		
		#*****  Replacement *****#
		replacement_demands = False
		
		replacement_demand_list = []
		replacement_demand_32_total = 0
		replacement_demand_34_total = 0
		replacement_demand_36_total = 0
		replacement_demand_38_total = 0
		replacement_demand_40_total = 0
		replacement_demand_42_total = 0
		replacement_demand_44_total = 0
		
		replacement_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','replacement')])
		
		if replacement_demands:
			replacement_demand_list = []
			for demand in replacement_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (270, 271, 272, 273, 274, 275, 276))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Replacement',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 270 else '',
							'34' : line.product_qty if line.product_id.id == 271 else '',
							'36' : line.product_qty if line.product_id.id == 272 else '',
							'38' : line.product_qty if line.product_id.id == 273 else '',
							'40' : line.product_qty if line.product_id.id == 274 else '',
							'42' : line.product_qty if line.product_id.id == 275 else '',
							'44' : line.product_qty if line.product_id.id == 276 else '',
						})
						replacement_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 270:
							replacement_demand_32_total = replacement_demand_32_total + line.product_qty
						if line.product_id.id == 271:
							replacement_demand_34_total = replacement_demand_34_total + line.product_qty
						if line.product_id.id == 272:
							replacement_demand_36_total = replacement_demand_36_total + line.product_qty
						if line.product_id.id == 273:
							replacement_demand_38_total = replacement_demand_38_total + line.product_qty
						if line.product_id.id == 274:
							replacement_demand_40_total = replacement_demand_40_total + line.product_qty
						if line.product_id.id == 275:
							replacement_demand_42_total = replacement_demand_42_total + line.product_qty
						if line.product_id.id == 276:
							replacement_demand_44_total = replacement_demand_44_total + line.product_qty	
			
		
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_trouser')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			'New_Demands' : new_demand_list,
			'New_Demand_Total': {'total_32': new_demand_32_total, 'total_34' : new_demand_34_total, 'total_36' : new_demand_36_total, 'total_38' : new_demand_38_total, 'total_40' : new_demand_40_total,'total_42' : new_demand_42_total,'total_44' : new_demand_44_total},
			'Complain_Demands' : complain_demand_list,
			'Complain_Demand_Total': {'total_32': complain_demand_32_total, 'total_34' : complain_demand_34_total, 'total_36' : complain_demand_36_total, 'total_38' : complain_demand_38_total, 'total_40' : complain_demand_40_total,'total_42' : complain_demand_42_total,'total_44' : complain_demand_44_total},
			'Add_Guard_Demands' : add_guard_demand_list,
			'Add_Guard_Demand_Total': {'total_32': add_guard_demand_32_total, 'total_34' : add_guard_demand_34_total, 'total_36' : add_guard_demand_36_total, 'total_38' : add_guard_demand_38_total, 'total_40' : add_guard_demand_40_total,'total_42' : add_guard_demand_42_total,'total_44' : add_guard_demand_44_total},
			'Replacement_Demands' : replacement_demand_list,
			'Replacement_Demand_Total': {'total_32': replacement_demand_32_total, 'total_34' : replacement_demand_34_total, 'total_36' : replacement_demand_36_total, 'total_38' : replacement_demand_38_total, 'total_40' : replacement_demand_40_total,'total_42' : replacement_demand_42_total,'total_44' : replacement_demand_44_total},
			"get_date_formate" : self.get_date_formate,
		}
		
		
