# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError
from odoo.osv.expression import AND , OR

class Seal(models.Model):
    _name = 'seal'
    _description = "Seal"
    
    seal_no = fields.Char('Seal No')
    seal_owner = fields.Selection([('shipper','Shipper'),
                                   ('shipping_line','Shipping Line'),
                                   ('customs','Customs'),
                                   ('clearance_com','Clearance Com'),
                                   ('third_party','Third Party'),
                                   ('other','Other')],string='Seal Owner')
    note = fields.Text('Note')
    is_smart_seal = fields.Boolean ('Is Smart Seal (GPS)')
    
    
   
#     @api.model_create_multi
#     @api.returns('self', lambda value:value.id)
#     def create(self, vals_list):
#         for val in vals_list:
#             val['name'] = self.env['ir.sequence'].next_by_code('job.seq')
#         return super(Job, self).create(vals_list)
    
    
    
   
    
  
        
