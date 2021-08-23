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


class ReportUniform(models.AbstractModel):
	_name = 'report.sos_uniform.report_uniform'
	_description = 'SOS Uniform Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	#def _get_report_values(self, docids, data=None):
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
		new_demand_46_total = 0
		new_demand_48_total = 0
		new_demand_50_total = 0
		
		#***** New Deployments *****#
		new_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','new_deployment')])
		
		if new_demands:
			new_demand_list = []
			for demand in new_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (236, 237,238,239,240,241,242,243,244,245))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'New Deployment',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 236 else '',
							'34' : line.product_qty if line.product_id.id == 237 else '',
							'36' : line.product_qty if line.product_id.id == 238 else '',
							'38' : line.product_qty if line.product_id.id == 239 else '',
							'40' : line.product_qty if line.product_id.id == 240 else '',
							'42' : line.product_qty if line.product_id.id == 241 else '',
							'44' : line.product_qty if line.product_id.id == 242 else '',
							'46' : line.product_qty if line.product_id.id == 243 else '',
							'48' : line.product_qty if line.product_id.id == 244 else '',
							'50' : line.product_qty if line.product_id.id == 245 else '',
						})
						new_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 236:
							new_demand_32_total = new_demand_32_total + line.product_qty
						if line.product_id.id == 237:
							new_demand_34_total = new_demand_34_total + line.product_qty
						if line.product_id.id == 238:
							new_demand_36_total = new_demand_36_total + line.product_qty
						if line.product_id.id == 239:
							new_demand_38_total = new_demand_38_total + line.product_qty
						if line.product_id.id == 240:
							new_demand_40_total = new_demand_40_total + line.product_qty
						if line.product_id.id == 241:
							new_demand_42_total = new_demand_42_total + line.product_qty
						if line.product_id.id == 242:
							new_demand_44_total = new_demand_44_total + line.product_qty
						if line.product_id.id == 243:
							new_demand_46_total = new_demand_46_total + line.product_qty
						if line.product_id.id == 244:
							new_demand_48_total = new_demand_48_total + line.product_qty
						if line.product_id.id == 245:
							new_demand_50_total = new_demand_50_total + line.product_qty
							
							
		
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
		complain_demand_46_total = 0
		complain_demand_48_total = 0
		complain_demand_50_total = 0
		
		
		
		complain_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','complain')])
		
		if complain_demands:
			complain_demand_list = []
			for demand in complain_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (236, 237,238,239,240,241,242,243,244,245))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Complain',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 236 else '',
							'34' : line.product_qty if line.product_id.id == 237 else '',
							'36' : line.product_qty if line.product_id.id == 238 else '',
							'38' : line.product_qty if line.product_id.id == 239 else '',
							'40' : line.product_qty if line.product_id.id == 240 else '',
							'42' : line.product_qty if line.product_id.id == 241 else '',
							'44' : line.product_qty if line.product_id.id == 242 else '',
							'46' : line.product_qty if line.product_id.id == 243 else '',
							'48' : line.product_qty if line.product_id.id == 244 else '',
							'50' : line.product_qty if line.product_id.id == 245 else '',
						})
						complain_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 236:
							complain_demand_32_total = complain_demand_32_total + line.product_qty
						if line.product_id.id == 237:
							complain_demand_34_total = complain_demand_34_total + line.product_qty
						if line.product_id.id == 238:
							complain_demand_36_total = complain_demand_36_total + line.product_qty
						if line.product_id.id == 239:
							complain_demand_38_total = complain_demand_38_total + line.product_qty
						if line.product_id.id == 240:
							complain_demand_40_total = complain_demand_40_total + line.product_qty
						if line.product_id.id == 241:
							complain_demand_42_total = complain_demand_42_total + line.product_qty
						if line.product_id.id == 242:
							complain_demand_44_total = complain_demand_44_total + line.product_qty
						if line.product_id.id == 243:
							complain_demand_46_total = complain_demand_46_total + line.product_qty
						if line.product_id.id == 244:
							complain_demand_48_total = complain_demand_48_total + line.product_qty
						if line.product_id.id == 245:
							complain_demand_50_total = complain_demand_50_total + line.product_qty
		
		#***** Additional Guards *****#
		add_guard_demands = False
		add_guard_demand_list = []
		
		add_guard_demand_32_total = 0
		add_guard_demand_34_total = 0
		add_guard_demand_36_total = 0
		add_guard_demand_38_total = 0
		add_guard_demand_40_total = 0
		add_guard_demand_42_total = 0
		add_guard_demand_44_total = 0
		add_guard_demand_46_total = 0
		add_guard_demand_48_total = 0
		add_guard_demand_50_total = 0
		
		
		
		add_guard_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','additional_guard')])
		
		if add_guard_demands:
			add_guard_demand_list = []
			for demand in add_guard_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (236, 237,238,239,240,241,242,243,244,245))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Additional Guard',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 236 else '',
							'34' : line.product_qty if line.product_id.id == 237 else '',
							'36' : line.product_qty if line.product_id.id == 238 else '',
							'38' : line.product_qty if line.product_id.id == 239 else '',
							'40' : line.product_qty if line.product_id.id == 240 else '',
							'42' : line.product_qty if line.product_id.id == 241 else '',
							'44' : line.product_qty if line.product_id.id == 242 else '',
							'46' : line.product_qty if line.product_id.id == 243 else '',
							'48' : line.product_qty if line.product_id.id == 244 else '',
							'50' : line.product_qty if line.product_id.id == 245 else '',
						})
						add_guard_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 236:
							add_guard_demand_32_total = add_guard_demand_32_total + line.product_qty
						if line.product_id.id == 237:
							add_guard_demand_34_total = add_guard_demand_34_total + line.product_qty
						if line.product_id.id == 238:
							add_guard_demand_36_total = add_guard_demand_36_total + line.product_qty
						if line.product_id.id == 239:
							add_guard_demand_38_total = add_guard_demand_38_total + line.product_qty
						if line.product_id.id == 240:
							add_guard_demand_40_total = add_guard_demand_40_total + line.product_qty
						if line.product_id.id == 241:
							add_guard_demand_42_total = add_guard_demand_42_total + line.product_qty
						if line.product_id.id == 242:
							add_guard_demand_44_total = add_guard_demand_44_total + line.product_qty
						if line.product_id.id == 243:
							add_guard_demand_46_total = add_guard_demand_46_total + line.product_qty
						if line.product_id.id == 244:
							add_guard_demand_48_total = add_guard_demand_48_total + line.product_qty
						if line.product_id.id == 245:
							add_guard_demand_50_total = add_guard_demand_50_total + line.product_qty					
		
		
		
		#***** Replacement *****#
		replacement_demands = False
		replacement_demand_list = []
		
		replacement_demand_32_total = 0
		replacement_demand_34_total = 0
		replacement_demand_36_total = 0
		replacement_demand_38_total = 0
		replacement_demand_40_total = 0
		replacement_demand_42_total = 0
		replacement_demand_44_total = 0
		replacement_demand_46_total = 0
		replacement_demand_48_total = 0
		replacement_demand_50_total = 0
		
		
		
		replacement_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','replacement')])
		
		if replacement_demands:
			replacement_demand_list = []
			for demand in replacement_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (236, 237,238,239,240,241,242,243,244,245))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Replacement',
							'demand_no' : demand.name,
							'32' : line.product_qty if line.product_id.id == 236 else '',
							'34' : line.product_qty if line.product_id.id == 237 else '',
							'36' : line.product_qty if line.product_id.id == 238 else '',
							'38' : line.product_qty if line.product_id.id == 239 else '',
							'40' : line.product_qty if line.product_id.id == 240 else '',
							'42' : line.product_qty if line.product_id.id == 241 else '',
							'44' : line.product_qty if line.product_id.id == 242 else '',
							'46' : line.product_qty if line.product_id.id == 243 else '',
							'48' : line.product_qty if line.product_id.id == 244 else '',
							'50' : line.product_qty if line.product_id.id == 245 else '',
						})
						replacement_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 236:
							replacement_demand_32_total = replacement_demand_32_total + line.product_qty
						if line.product_id.id == 237:
							replacement_demand_34_total = replacement_demand_34_total + line.product_qty
						if line.product_id.id == 238:
							replacement_demand_36_total = replacement_demand_36_total + line.product_qty
						if line.product_id.id == 239:
							replacement_demand_38_total = replacement_demand_38_total + line.product_qty
						if line.product_id.id == 240:
							replacement_demand_40_total = replacement_demand_40_total + line.product_qty
						if line.product_id.id == 241:
							replacement_demand_42_total = replacement_demand_42_total + line.product_qty
						if line.product_id.id == 242:
							replacement_demand_44_total = replacement_demand_44_total + line.product_qty
						if line.product_id.id == 243:
							replacement_demand_46_total = replacement_demand_46_total + line.product_qty
						if line.product_id.id == 244:
							replacement_demand_48_total = replacement_demand_48_total + line.product_qty
						if line.product_id.id == 245:
							replacement_demand_50_total = replacement_demand_50_total + line.product_qty					
		
							
										
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_uniform')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			'New_Demands' : new_demand_list,
			'New_Demand_Total': {'total_32': new_demand_32_total, 'total_34' : new_demand_34_total, 'total_36' : new_demand_36_total, 'total_38' : new_demand_38_total, 'total_40' : new_demand_40_total,'total_42' : new_demand_42_total,'total_44' : new_demand_44_total,'total_46' : new_demand_46_total,'total_48' : new_demand_48_total,'total_50' : new_demand_50_total},
			'Complain_Demands' : complain_demand_list,
			'Complain_Demand_Total': {'total_32': complain_demand_32_total, 'total_34' : complain_demand_34_total, 'total_36' : complain_demand_36_total, 'total_38' : complain_demand_38_total, 'total_40' : complain_demand_40_total,'total_42' : complain_demand_42_total,'total_44' : complain_demand_44_total,'total_46' : complain_demand_46_total,'total_48' : complain_demand_48_total,'total_50' : complain_demand_50_total},
			'Add_Guard_Demands' : add_guard_demand_list,
			'Add_Guard_Demand_Total': {'total_32': add_guard_demand_32_total, 'total_34' : add_guard_demand_34_total, 'total_36' : add_guard_demand_36_total, 'total_38' : add_guard_demand_38_total, 'total_40' : add_guard_demand_40_total,'total_42' : add_guard_demand_42_total,'total_44' : add_guard_demand_44_total,'total_46' : add_guard_demand_46_total,'total_48' : add_guard_demand_48_total,'total_50' : add_guard_demand_50_total},
			'Replacement_Demands' : replacement_demand_list,
			'Replacement_Demand_Total': {'total_32': replacement_demand_32_total, 'total_34' : replacement_demand_34_total, 'total_36' : replacement_demand_36_total, 'total_38' : replacement_demand_38_total, 'total_40' : replacement_demand_40_total,'total_42' : replacement_demand_42_total,'total_44' : replacement_demand_44_total,'total_46' : replacement_demand_46_total,'total_48' : replacement_demand_48_total,'total_50' : replacement_demand_50_total},
			"get_date_formate" : self.get_date_formate,
		}
		
		
