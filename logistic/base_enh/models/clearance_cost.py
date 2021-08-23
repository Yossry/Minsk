# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class ClearancelinsuCost(models.Model):
    _name = 'clearance.cost.line'
    _description = "ClearancelinsuCost"
    
    from_truck = fields.Integer('From')
    to_truck = fields.Integer('To')
    cost = fields.Monetary(string="Cost")
    cost_id = fields.Many2one('clearance.cost',ondelete='cascade', string="Clearance Cost")
    currency_id = fields.Many2one('res.currency', string="Currency")
    @api.constrains('from_truck','to_truck')
    def _check_additional_cost(self):
        for rec in self:
            if rec.from_truck > rec.to_truck:
                raise Warning(_("From Value must be less or equal than To Value"))
            
class ClearanceCost(models.Model):
    _name = 'clearance.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'qut_number'
    _description = "ClearanceCost"
    
   
    qut_number =fields.Char('Quotation Number',required=True)
    is_next = fields.Boolean('Is Next Price',compute="_compute_is_expired")
    is_expired = fields.Boolean('Is Expired Price',compute="_compute_is_expired")
    shipment_method = fields.Selection([('all_in', 'All In'), ('sea_freight', 'Sea freight'), ('land_freight', 'Land Freight'), ('air_freight', 'Air Freight'), ('clearance', 'Clearance')])
    shipment_type = fields.Selection([ ('import', 'Import'), ('export', 'Export')])
    partner_id = fields.Many2one('res.partner',string="Clearance",domain=[('is_clearance_company', '=', True)])
    customs_id = fields.Many2one('res.partner',string="Customs point",domain=[('is_customs_point', '=', True)])
    partner_point_ids = fields.Many2many('res.partner',string="Point Contact",compute="_compute_partner_point_ids")
    customs_declaration_id = fields.Many2one('customs.declaration',string="Customs Declaration")
    date = fields.Date('Date')
    price = fields.Monetary()
    cost_line_ids = fields.One2many('clearance.cost.line','cost_id',string="Additional Cost")
    total = fields.Monetary('Total', compute='_compute_total',store=True)
    note = fields.Text()
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    currency_id = fields.Many2one('res.currency', string="Currency")
    active=fields.Boolean(default=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms",
                                      related='partner_id.property_supplier_payment_term_id')
    #Smart buttons
    @api.multi  
    def call_job(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('job', 'view_job__tree')[1]
            form_res = mod_obj.get_object_reference('job', 'view_job_form')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('job'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'job',  
            'view_id': False,  
            'views': [(tree_res, 'tree'),(form_res, 'form')], 
            'domain': [('customs_dec_id.id', '=', self.customs_declaration_id.id)], 
            'target': 'current',  
               }      
    @api.multi  
    def call_sale_inquiry(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('sale.inquiry', 'view_inquiry_tree')[1]
            form_res = mod_obj.get_object_reference('sale.inquiry', 'view_inquiry_form')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('sale.inquiry'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'sale.inquiry',  
            'view_id': False,  
            'views': [(tree_res, 'tree'),(form_res, 'form')], 
            'domain': [('customs_dec_id.id', '=', self.customs_declaration_id.id)], 
            'target': 'current',  
               }
    
    @api.onchange('partner_id')
    def clear_company_related_data(self):
        """
        Clear custom_declaration_id, from_date, to_date, 
        shipment_type,qut_number once partner_id changed 
        or erased.
        """
        for rec in self:
            rec.qut_number=u''
            rec.shipment_type=u''
            rec.from_date=u''
            rec.to_date=u''
            rec.customs_declaration_id=u''
    
    
    @api.constrains('from_date','to_date')
    def date_from_to(self):
        """To date greater than From date"""
        for rec in self:
            if rec.from_date and rec.to_date and rec.from_date > rec.to_date:
                raise Warning("'From Date' should be less or equal 'To date'!")
    
   
    
    @api.onchange('shipment_method')
    def onchange_shipment_method(self):
        self.shipment_type = False
        self.customs_deceleration_id = False
        
        
        
    @api.onchange('partner_id')
    def erse_price_trans(self):
        """"Erase price once quotation OR Shipper changed"""
        self.price= 0
        self.date = False
        self.customs_id = False
        self.cost_line_ids = False
    
    @api.multi
    @api.depends('to_date','from_date')
    def _compute_is_expired(self):
        for rec in self:
            if rec.to_date and rec.to_date < fields.Date.today():
               rec.is_expired = True 
            else:
               rec.is_expired = False
            if rec.from_date and rec.from_date > fields.Date.today():
               rec.is_next = True 
            else:
               rec.is_next = False
            
    @api.depends('customs_id')
    def _compute_partner_point_ids(self):
        for rec in self:
            if rec.customs_id:
                rec.partner_point_ids = self.env['res.partner'].with_context(from_customs_filter=False).search([('customs_id','=',rec.customs_id.id)])
            else:
                rec.partner_point_ids = [(5,0,0)]
    @api.depends('price','cost_line_ids','cost_line_ids.cost')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.price + sum(rec.cost_line_ids.mapped('cost')+[0])
    

            
    
    
    
        
        
    