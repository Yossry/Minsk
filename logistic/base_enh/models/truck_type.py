# -*- coding: utf-8 -*-

from odoo import models, fields, api


class truckType(models.Model):
    _name = 'truck.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "truckType"
    
    name = fields.Char('Size',required=True)
    note = fields.Char('Note')
    image = fields.Binary(attachment=True)
    active=fields.Boolean(default=True)
    type = fields.Many2many('truck.type.selections')
    
    @api.multi  
    def call_truck_type_selection(self):  
        mod_obj = self.env['ir.model.data']
        try:
#             kanban_res = mod_obj.get_object_reference('base_enh', 'truck_type_selections_list_view')[1]
            tree_res = mod_obj.get_object_reference('base_enh', 'purchase_order_tree')[1]
            form_res = mod_obj.get_object_reference('base_enh', 'purchase_order_tree')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = kanban_res= False
        return {  
            'name': ('Truck Type Selections'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'truck.type.selections',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form')], 
            'domain': [('id','in',self.type.ids)], 
            'target': 'current',  
               }
        
class TruckTypeSelections(models.Model):
    _name='truck.type.selections'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description='selections of truck type'
    
    name=fields.Char('Name')
    active=fields.Boolean(default=True)