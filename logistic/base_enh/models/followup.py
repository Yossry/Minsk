# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Followup(models.Model):
    _name = 'followup'
    _description = "Followup"
    
    is_load_from_depot = fields.Boolean('Is Loaded From Depot')
    depot_date = fields.Datetime('Loaded from Depot Datetime')
    depot_note = fields.Text('Loaded from Depot Note')
    
    arrived_to_shipper = fields.Boolean('Arrived to Shipper')
    arrived_shipper_date = fields.Datetime('Arrived To Shipper Datetime')
    arrived_shipper_note = fields.Text('Arrived To Shipper Note')
    
    depart_from_shipper =  fields.Boolean('Depart from Shipper')
    depart_shipper_date = fields.Datetime('Depart from Shipper Datetime')
    depart_shipper_note = fields.Text('Depart from Shipper Note')
    
    terminal_active =  fields.Boolean('Terminal Active')
    terminal_active_date = fields.Datetime('Terminal Active Datetime')
    terminal_active_note = fields.Text('Terminal Active Note')
    
    misfer_registered =  fields.Boolean('Misfer Registered')
    misfer_date = fields.Datetime('Misfer Datetime')
    misfer_note = fields.Text('Misfer Note')
    
    xray_registered =  fields.Boolean('X-Ray Registered')
    xray_date = fields.Datetime('X-Ray Datetime')
    xray_note = fields.Text('X-Ray Note')
    
    terminal_gate_in =  fields.Boolean('Terminal Gate In')
    terminal_gate_date = fields.Datetime('Terminal Gate Datetime')
    terminal_gate_note = fields.Text('Terminal Gate Note')
    
    terminal_registered =  fields.Boolean('Terminal Registered')
    terminal_registered_date = fields.Datetime('Terminal Registered Datetime')
    terminal_registered_note = fields.Text('Terminal Registered Note')
    
    loaded_to_vessel =  fields.Boolean('Loaded to Vessel')
    loaded_vessel_date = fields.Datetime('Loaded Vessel Datetime')
    loaded_vessel_note = fields.Text('Loaded Vessel Note')
    
#     @api.model_create_multi
#     @api.returns('self', lambda value:value.id)
#     def create(self, vals_list):
#         for val in vals_list:
#             val['name'] = self.env['ir.sequence'].next_by_code('job.seq')
#         return super(Job, self).create(vals_list)
    
    
    
   
    
  
        
