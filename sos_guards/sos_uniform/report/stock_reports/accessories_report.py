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



class ReportAccessories(models.AbstractModel):
	_name = 'report.sos_uniform.report_accessories'
	_description = 'Uniform Accessories Report'
	
	def get_date_formate(self,sdate):
		ss = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')
			
	@api.model
	def	get_report_values(self, docids, data=None):
		
		date_from = data['form']['date_from'] and data['form']['date_from']
		date_to = data['form']['date_to'] and data['form']['date_to']
		
		new_demands = False
		
		new_demand_list = []
		new_demand_whistle_dori_total = 0
		new_demand_metal_detector_total = 0
		new_demand_torch_total = 0
		new_demand_cap_total = 0
		new_demand_belt_total = 0
		new_demand_garmal_total = 0
		new_demand_scarf_total = 0
		new_demand_boot_anklet_total = 0
		new_demand_pistol_pouch_total = 0
		new_demand_ammunition_belt_total = 0
		new_demand_shilling_total = 0
		new_demand_jersey_total = 0
		new_demand_jacket_total = 0
		new_demand_vehicle_mirror_total = 0
				
		#***** New Deployments *****#
		new_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','new_deployment')])
		
		if new_demands:
			new_demand_list = []
			for demand in new_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (66,71,126,252,253,254,256,257,258,259,260,302,303,313))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'New Deployment',
							'demand_no' : demand.name,
							'whistle_dori' : line.product_qty if line.product_id.id == 66 else '',
							'metal_detector' : line.product_qty if line.product_id.id == 71 else '',
							'torch' : line.product_qty if line.product_id.id == 126 else '',
							'cap' : line.product_qty if line.product_id.id == 252 else '',
							'belt' : line.product_qty if line.product_id.id == 253 else '',
							'garmal' : line.product_qty if line.product_id.id == 254 else '',
							'scarf' : line.product_qty if line.product_id.id == 256 else '',
							'boot_anklet' : line.product_qty if line.product_id.id == 257 else '',
							'pistol_pouch' : line.product_qty if line.product_id.id == 258 else '',
							'ammunition_belt' : line.product_qty if line.product_id.id ==259  else '',
							'shilling' : line.product_qty if line.product_id.id == 260 else '',
							'jersey' : line.product_qty if line.product_id.id == 302 else '',
							'jacket' : line.product_qty if line.product_id.id == 303 else '',
							'vehicle_mirror' : line.product_qty if line.product_id.id == 313 else '',
						})
						new_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 66:
							new_demand_whistle_dori_total = new_demand_whistle_dori_total + line.product_qty
						if line.product_id.id == 71:
							new_demand_metal_detector_total = new_demand_metal_detector_total + line.product_qty
						if line.product_id.id == 126:
							new_demand_torch_total = new_demand_torch_total + line.product_qty
						if line.product_id.id == 252:
							new_demand_cap_total = new_demand_cap_total + line.product_qty	
						if line.product_id.id == 253:
							new_demand_belt_total = new_demand_belt_total + line.product_qty
						if line.product_id.id == 254:
							new_demand_garmal_total = new_demand_garmal_total + line.product_qty
						if line.product_id.id == 256:
							new_demand_scarf_total = new_demand_scarf_total + line.product_qty
						if line.product_id.id == 257:
							new_demand_boot_anklet_total = new_demand_boot_anklet_total + line.product_qty
						if line.product_id.id == 258:
							new_demand_pistol_pouch_tota = new_demand_pistol_pouch_tota + line.product_qty
						if line.product_id.id == 259:
							new_demand_ammunition_belt_total = new_demand_ammunition_belt_total + line.product_qty
						if line.product_id.id == 260:
							new_demand_shilling_total = new_demand_shilling_total + line.product_qty
						if line.product_id.id == 302:
							new_demand_jersey_total =new_demand_jersey_total + line.product_qty
						if line.product_id.id == 303:
							new_demand_jacket_total = new_demand_jacket_total + line.product_qty
						if line.product_id.id == 313:
							new_demand_vehicle_mirror_total = new_demand_vehicle_mirror_total + line.product_qty
		
		
		#***** Complain *****#
		complain_demands = False
		
		complain_demand_list = []
		complain_demand_whistle_dori_total = 0
		complain_demand_metal_detector_total = 0
		complain_demand_torch_total = 0
		complain_demand_cap_total = 0
		complain_demand_belt_total = 0
		complain_demand_garmal_total = 0
		complain_demand_scarf_total = 0
		complain_demand_boot_anklet_total = 0
		complain_demand_pistol_pouch_total = 0
		complain_demand_ammunition_belt_total = 0
		complain_demand_shilling_total = 0
		complain_demand_jersey_total = 0
		complain_demand_jacket_total = 0
		complain_demand_vehicle_mirror_total = 0
		
		complain_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','complain')])
		
		if complain_demands:
			complain_demand_list = []
			for demand in complain_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (66,71,126,252,253,254,256,257,258,259,260,302,303,313))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Complain',
							'demand_no' : demand.name,
							'whistle_dori' : line.product_qty if line.product_id.id == 66 else '',
							'metal_detector' : line.product_qty if line.product_id.id == 71 else '',
							'torch' : line.product_qty if line.product_id.id == 126 else '',
							'cap' : line.product_qty if line.product_id.id == 252 else '',
							'belt' : line.product_qty if line.product_id.id == 253 else '',
							'garmal' : line.product_qty if line.product_id.id == 254 else '',
							'scarf' : line.product_qty if line.product_id.id == 256 else '',
							'boot_anklet' : line.product_qty if line.product_id.id == 257 else '',
							'pistol_pouch' : line.product_qty if line.product_id.id == 258 else '',
							'ammunition_belt' : line.product_qty if line.product_id.id ==259  else '',
							'shilling' : line.product_qty if line.product_id.id == 260 else '',
							'jersey' : line.product_qty if line.product_id.id == 302 else '',
							'jacket' : line.product_qty if line.product_id.id == 303 else '',
							'vehicle_mirror' : line.product_qty if line.product_id.id == 313 else '',
						})
						complain_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 66:
							complain_demand_whistle_dori_total = complain_demand_whistle_dori_total + line.product_qty
						if line.product_id.id == 71:
							complain_demand_metal_detector_total = complain_demand_metal_detector_total + line.product_qty
						if line.product_id.id == 126:
							complain_demand_torch_total = complain_demand_torch_total + line.product_qty
						if line.product_id.id == 252:
							complain_demand_cap_total = complain_demand_cap_total + line.product_qty	
						if line.product_id.id == 253:
							complain_demand_belt_total = complain_demand_belt_total + line.product_qty
						if line.product_id.id == 254:
							complain_demand_garmal_total = complain_demand_garmal_total + line.product_qty
						if line.product_id.id == 256:
							complain_demand_scarf_total = complain_demand_scarf_total + line.product_qty
						if line.product_id.id == 257:
							complain_demand_boot_anklet_total = complain_demand_boot_anklet_total + line.product_qty
						if line.product_id.id == 258:
							complain_demand_pistol_pouch_tota = complain_demand_pistol_pouch_tota + line.product_qty
						if line.product_id.id == 259:
							complain_demand_ammunition_belt_total = complain_demand_ammunition_belt_total + line.product_qty
						if line.product_id.id == 260:
							complain_demand_shilling_total = complain_demand_shilling_total + line.product_qty
						if line.product_id.id == 302:
							complain_demand_jersey_total = complain_demand_jersey_total + line.product_qty
						if line.product_id.id == 303:
							complain_demand_jacket_total = complain_demand_jacket_total + line.product_qty
						if line.product_id.id == 313:
							complain_demand_vehicle_mirror_total = complain_demand_vehicle_mirror_total + line.product_qty
							
		
		#***** Additional Guards *****#
		add_guard_demands = False
		
		add_guard_demand_list = []
		add_guard_demand_whistle_dori_total = 0
		add_guard_demand_metal_detector_total = 0
		add_guard_demand_torch_total = 0
		add_guard_demand_cap_total = 0
		add_guard_demand_belt_total = 0
		add_guard_demand_garmal_total = 0
		add_guard_demand_scarf_total = 0
		add_guard_demand_boot_anklet_total = 0
		add_guard_demand_pistol_pouch_total = 0
		add_guard_demand_ammunition_belt_total = 0
		add_guard_demand_shilling_total = 0
		add_guard_demand_jersey_total = 0
		add_guard_demand_jacket_total = 0
		add_guard_demand_vehicle_mirror_total = 0
		
		add_guard_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','additional_guard')])
		
		if add_guard_demands:
			add_guard_demand_list = []
			for demand in add_guard_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (66,71,126,252,253,254,256,257,258,259,260,302,303,313))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Additional Guard',
							'demand_no' : demand.name,
							'whistle_dori' : line.product_qty if line.product_id.id == 66 else '',
							'metal_detector' : line.product_qty if line.product_id.id == 71 else '',
							'torch' : line.product_qty if line.product_id.id == 126 else '',
							'cap' : line.product_qty if line.product_id.id == 252 else '',
							'belt' : line.product_qty if line.product_id.id == 253 else '',
							'garmal' : line.product_qty if line.product_id.id == 254 else '',
							'scarf' : line.product_qty if line.product_id.id == 256 else '',
							'boot_anklet' : line.product_qty if line.product_id.id == 257 else '',
							'pistol_pouch' : line.product_qty if line.product_id.id == 258 else '',
							'ammunition_belt' : line.product_qty if line.product_id.id ==259  else '',
							'shilling' : line.product_qty if line.product_id.id == 260 else '',
							'jersey' : line.product_qty if line.product_id.id == 302 else '',
							'jacket' : line.product_qty if line.product_id.id == 303 else '',
							'vehicle_mirror' : line.product_qty if line.product_id.id == 313 else '',
						})
						add_guard_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 66:
							add_guard_demand_whistle_dori_total = add_guard_demand_whistle_dori_total + line.product_qty
						if line.product_id.id == 71:
							add_guard_demand_metal_detector_total = add_guard_demand_metal_detector_total + line.product_qty
						if line.product_id.id == 126:
							add_guard_demand_torch_total = add_guard_demand_torch_total + line.product_qty
						if line.product_id.id == 252:
							add_guard_demand_cap_total = add_guard_demand_cap_total + line.product_qty	
						if line.product_id.id == 253:
							add_guard_demand_belt_total = add_guard_demand_belt_total + line.product_qty
						if line.product_id.id == 254:
							add_guard_demand_garmal_total = add_guard_demand_garmal_total + line.product_qty
						if line.product_id.id == 256:
							add_guard_demand_scarf_total = add_guard_demand_scarf_total + line.product_qty
						if line.product_id.id == 257:
							add_guard_demand_boot_anklet_total = add_guard_demand_boot_anklet_total + line.product_qty
						if line.product_id.id == 258:
							add_guard_demand_pistol_pouch_tota = add_guard_demand_pistol_pouch_tota + line.product_qty
						if line.product_id.id == 259:
							add_guard_demand_ammunition_belt_total = add_guard_demand_ammunition_belt_total + line.product_qty
						if line.product_id.id == 260:
							add_guard_demand_shilling_total = add_guard_demand_shilling_total + line.product_qty
						if line.product_id.id == 302:
							add_guard_demand_jersey_total = add_guard_demand_jersey_total + line.product_qty
						if line.product_id.id == 303:
							add_guard_demand_jacket_total = add_guard_demand_jacket_total + line.product_qty
						if line.product_id.id == 313:
							add_guard_demand_vehicle_mirror_total = add_guard_demand_vehicle_mirror_total + line.product_qty									
		
		
		#***** Replacement *****#
		replacement_demands = False
		
		replacement_demand_list = []
		replacement_demand_whistle_dori_total = 0
		replacement_demand_metal_detector_total = 0
		replacement_demand_torch_total = 0
		replacement_demand_cap_total = 0
		replacement_demand_belt_total = 0
		replacement_demand_garmal_total = 0
		replacement_demand_scarf_total = 0
		replacement_demand_boot_anklet_total = 0
		replacement_demand_pistol_pouch_total = 0
		replacement_demand_ammunition_belt_total = 0
		replacement_demand_shilling_total = 0
		replacement_demand_jersey_total = 0
		replacement_demand_jacket_total = 0
		replacement_demand_vehicle_mirror_total = 0
		
		replacement_demands = self.env['sos.uniform.demand'].search([('date','>=',date_from),('date','<=',date_to),('dm_type','=','replacement')])
		
		if replacement_demands:
			replacement_demand_list = []
			for demand in replacement_demands: 
				dispatch_lines = demand.uniform_dispatch_line.filtered(lambda x: x.product_id.id in (66,71,126,252,253,254,256,257,258,259,260,302,303,313))
				if dispatch_lines:
					for line in dispatch_lines:
						res=({
							'date': demand.date,
							'post': demand.post_id and demand.post_id.name or False,
							'center': demand.center_id and demand.center_id.name or False,
							'type': 'Replacement',
							'demand_no' : demand.name,
							'whistle_dori' : line.product_qty if line.product_id.id == 66 else '',
							'metal_detector' : line.product_qty if line.product_id.id == 71 else '',
							'torch' : line.product_qty if line.product_id.id == 126 else '',
							'cap' : line.product_qty if line.product_id.id == 252 else '',
							'belt' : line.product_qty if line.product_id.id == 253 else '',
							'garmal' : line.product_qty if line.product_id.id == 254 else '',
							'scarf' : line.product_qty if line.product_id.id == 256 else '',
							'boot_anklet' : line.product_qty if line.product_id.id == 257 else '',
							'pistol_pouch' : line.product_qty if line.product_id.id == 258 else '',
							'ammunition_belt' : line.product_qty if line.product_id.id ==259  else '',
							'shilling' : line.product_qty if line.product_id.id == 260 else '',
							'jersey' : line.product_qty if line.product_id.id == 302 else '',
							'jacket' : line.product_qty if line.product_id.id == 303 else '',
							'vehicle_mirror' : line.product_qty if line.product_id.id == 313 else '',
						})
						replacement_demand_list.append(res)
						
						##Totals
						if line.product_id.id == 66:
							replacement_demand_whistle_dori_total = replacement_demand_whistle_dori_total + line.product_qty
						if line.product_id.id == 71:
							replacement_demand_metal_detector_total = replacement_demand_metal_detector_total + line.product_qty
						if line.product_id.id == 126:
							replacement_demand_torch_total = replacement_demand_torch_total + line.product_qty
						if line.product_id.id == 252:
							replacement_demand_cap_total = replacement_demand_cap_total + line.product_qty	
						if line.product_id.id == 253:
							replacement_demand_belt_total = replacement_demand_belt_total + line.product_qty
						if line.product_id.id == 254:
							replacement_demand_garmal_total = replacement_demand_garmal_total + line.product_qty
						if line.product_id.id == 256:
							replacement_demand_scarf_total = replacement_demand_scarf_total + line.product_qty
						if line.product_id.id == 257:
							replacement_demand_boot_anklet_total = replacement_demand_boot_anklet_total + line.product_qty
						if line.product_id.id == 258:
							replacement_demand_pistol_pouch_tota = replacement_demand_pistol_pouch_tota + line.product_qty
						if line.product_id.id == 259:
							replacement_demand_ammunition_belt_total = replacement_demand_ammunition_belt_total + line.product_qty
						if line.product_id.id == 260:
							replacement_demand_shilling_total = replacement_demand_shilling_total + line.product_qty
						if line.product_id.id == 302:
							replacement_demand_jersey_total = replacement_demand_jersey_total + line.product_qty
						if line.product_id.id == 303:
							replacement_demand_jacket_total = replacement_demand_jacket_total + line.product_qty
						if line.product_id.id == 313:
							replacement_demand_vehicle_mirror_total = replacement_demand_vehicle_mirror_total + line.product_qty									
												
							
		
		report = self.env['ir.actions.report']._get_report_from_name('sos_uniform.report_accessories')
		return {
			"doc_ids": self._ids,
			"doc_model": report.model,
			"time": time,
			"data": data['form'],
			"docs": self,
			'New_Demands' : new_demand_list,
			'New_Demand_Total': {'total_whistle_dori': new_demand_whistle_dori_total, 'total_metal_detector' : new_demand_metal_detector_total, 'total_torch' : new_demand_torch_total, 'total_cap' : new_demand_cap_total, 'total_belt' : new_demand_belt_total,'total_garmal' : new_demand_garmal_total,'total_scarf' : new_demand_scarf_total,'total_boot_anklet' : new_demand_boot_anklet_total,'total_pistol_pouch' : new_demand_pistol_pouch_total,'total_ammunition_belt' : new_demand_ammunition_belt_total,'total_shilling' : new_demand_shilling_total,'total_jersey' : new_demand_jersey_total,'total_jacket':new_demand_jacket_total,'total_vehicle_mirror' : new_demand_vehicle_mirror_total},
			'Complain_Demands' :complain_demand_list,
			'Complain_Demand_Total': {'total_whistle_dori': complain_demand_whistle_dori_total, 'total_metal_detector' : complain_demand_metal_detector_total, 'total_torch' : complain_demand_torch_total, 'total_cap' : complain_demand_cap_total, 'total_belt' : complain_demand_belt_total,'total_garmal' : complain_demand_garmal_total,'total_scarf' : complain_demand_scarf_total,'total_boot_anklet' : complain_demand_boot_anklet_total,'total_pistol_pouch' : complain_demand_pistol_pouch_total,'total_ammunition_belt' : complain_demand_ammunition_belt_total,'total_shilling' : complain_demand_shilling_total,'total_jersey' : complain_demand_jersey_total,'total_jacket':complain_demand_jacket_total,'total_vehicle_mirror' : complain_demand_vehicle_mirror_total},
			'Add_Guard_Demands' : add_guard_demand_list,
			'Add_Guard_Demand_Total': {'total_whistle_dori': add_guard_demand_whistle_dori_total, 'total_metal_detector' : add_guard_demand_metal_detector_total, 'total_torch' : add_guard_demand_torch_total, 'total_cap' : add_guard_demand_cap_total, 'total_belt' : add_guard_demand_belt_total,'total_garmal' : add_guard_demand_garmal_total,'total_scarf' : add_guard_demand_scarf_total,'total_boot_anklet' : add_guard_demand_boot_anklet_total,'total_pistol_pouch' : add_guard_demand_pistol_pouch_total,'total_ammunition_belt' : add_guard_demand_ammunition_belt_total,'total_shilling' : add_guard_demand_shilling_total,'total_jersey' : add_guard_demand_jersey_total,'total_jacket':add_guard_demand_jacket_total,'total_vehicle_mirror' : add_guard_demand_vehicle_mirror_total},
			'Replacement_Demands' : replacement_demand_list,
			'Replacement_Demand_Total': {'total_whistle_dori': replacement_demand_whistle_dori_total, 'total_metal_detector' : replacement_demand_metal_detector_total, 'total_torch' : replacement_demand_torch_total, 'total_cap' : replacement_demand_cap_total, 'total_belt' : replacement_demand_belt_total,'total_garmal' : replacement_demand_garmal_total,'total_scarf' : replacement_demand_scarf_total,'total_boot_anklet' : replacement_demand_boot_anklet_total,'total_pistol_pouch' : replacement_demand_pistol_pouch_total,'total_ammunition_belt' : replacement_demand_ammunition_belt_total,'total_shilling' : replacement_demand_shilling_total,'total_jersey' : replacement_demand_jersey_total,'total_jacket':replacement_demand_jacket_total,'total_vehicle_mirror' : replacement_demand_vehicle_mirror_total},
			"get_date_formate" : self.get_date_formate,
		}
		
		
