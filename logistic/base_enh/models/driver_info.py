# -*- coding: utf-8 -*-
from odoo import models, fields, api

# This model to show driver/container/follow up details

class DriverInfo(models.Model):
    _name = 'driver.info'
    _description = "DriverInfo"
    
    partner_id = fields.Many2one('res.partner')
    name = fields.Char(related='partner_id.name')
    mobile = fields.Char(related='partner_id.mobile')
    plate_code = fields.Char(related='partner_id.plate_code')
    plate_number = fields.Char(related='partner_id.plate_number')
    is_original_document = fields.Boolean(inverse='orginal_dr_doc')
    job_driver_id = fields.Many2one ('job')
    container_no = fields.Integer('Container No', default=4)
    state = fields.Selection([('non', 'Non'), 
                                        ('truck', 'Truck'), 
                                        ('yard', 'Yard'),
                                        ('vessel', 'Vessel'), 
                                        ('other', 'Other')],string="Container Status")  
    followup_id = fields.Many2many ('followup',string='Follow Up')
    seal_id = fields.Many2many ('seal',string='Seal')
    
    container_size_ids = fields.One2many('sale.inquiry.container',
                                          inverse_name='driver_info_id',
                                         string= 'Container',
                                         related='job_driver_id.container_size_ids')
    
    @api.multi
    def orginal_dr_doc(self):
        if 'dont_check' not in self._context:
            for rec in self:
                driver_ids = self.search([('job_driver_id','=',rec.job_driver_id.id),('id','!=',rec.id)])
                if driver_ids:
                    driver_ids.with_context(dont_check = True).write({'is_original_document':not rec.is_original_document})
                
    
    
    
    
   
    
  
        
