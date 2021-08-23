# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import UserError
from os import linesep


class AirLineCost(models.Model):
    _name='air.line.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='air_line_comp_id'
    _description='Airline cost table'
    
    air_line_comp_id=fields.Many2one('res.partner', domain=[('is_air_line','=',True)], required=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms", 
                                      related='air_line_comp_id.property_supplier_payment_term_id')
    quot_no=fields.Char('Quotation Number', required=True)
    date=fields.Date('Date', required=True)
    active=fields.Boolean('Active', default=True)
    is_expired=fields.Boolean('Is Expired', compute='_compute_is_expired')
    is_next=fields.Boolean('Is Next', compute='_compute_is_next')
#   General Info fields 
    country_loading_id=fields.Many2one('res.country',required=True)
    state_loading_id = fields.Many2one('res.country.state', string="State Of Loading")
    city_loading_id = fields.Many2one('res.city', string="City Of Loading")
    place_loading_id = fields.Many2one('res.place', string="Place Of Loading", required=False)
    port_loading_id = fields.Many2one('port', string="POL", required=True)
    terminal_loading_id = fields.Many2one('res.place', string="Terminal of Loading", required=True)
    
    transt_time = fields.Integer(required=True)
    start_date = fields.Date('Start Date')
    expiry_date = fields.Date('Expiry Date')
    
    country_dest_id = fields.Many2one('res.country', string="Country Of Discharge", required=True)
    state_dest_id = fields.Many2one('res.country.state', string="State Of Discharge")
    city_dest_id = fields.Many2one('res.city', string="City Of Discharge")
    place_dest_id = fields.Many2one('res.place', string="Place Of Discharge")
    port_dest_id = fields.Many2one('port', string="POD", required=True)
    terminal_des_same_id = fields.Many2one('res.place', string="Terminal of Discharge")
    
    customer_id = fields.Many2one('res.partner',stirng='Named Account')
    fak = fields.Boolean('FAK',default=True)
    commodity_id = fields.Many2many('commodity')
    commodity_domain_ids = fields.Many2many('commodity', related='customer_id.commodity_ids')
    sci=fields.Selection([('c','C'),
                          ('x','X'),
                          ('td','TD'),
                          ('t1','T1'),
                          ('t2','T2'),
                          ('tf','TF')], string='SCI')
    main_harmonize=fields.Char('Main Harmonize')
    carrier_tariff_reference=fields.Char('Carrier Tariff Reference')
#   on2many fields
    air_line_cost_line_ds =fields.One2many('air.line.cost.line','air_line_cost_id') 
    air_line_add_cost_ds =fields.One2many('air.line.addit.cost','air_line_costt_id')
    air_line_note_cost_ds =fields.One2many('air.line.note','air_line_costt_id')
    currency_id=fields.Many2one('res.currency', 'Main Currency', default=lambda self: self.env.user.company_id.currency_id.id, readonly=True)

    
    
    @api.onchange('country_dest_id')
    def erase_country_des_related(self):
        for rec in self:
            rec.state_dest_id=u''
            rec.city_dest_id=u''
            rec.place_dest_id=u''
            rec.port_dest_id=u''
            rec.terminal_des_same_id=u''
   
    @api.onchange('state_dest_id')
    def erase_state_des_related(self):
        for rec in self:
            rec.city_dest_id=u''
            
    @api.onchange('city_dest_id')
    def erase_city_des_related(self):
        for rec in self:
            rec.place_dest_id=u''
    
    @api.onchange('port_dest_id')
    def erase_port_des_related(self):
        for rec in self:
            rec.terminal_des_same_id=u''

    @api.depends('start_date','expiry_date')
    def check_date(self):
        for rec in self:
            if rec.start_date and rec.expiry_date:
                if rec.start_date > rec.expiry_date:
                    raise UserError("'Start date' should be less or equal 'Expiry date'")
    
    @api.multi
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        for rec in self:
            if rec.expiry_date and rec.expiry_date < fields.Date.today():
               rec.is_expired = True 
            else:
               rec.is_expired = False
    
    @api.onchange('fak')
    def _onchange_fak(self):
        self.commodity_id = False
                   
    @api.multi
    @api.depends('start_date')
    def _compute_is_next(self):
        for rec in self:
            if rec.start_date and rec.start_date > fields.Date.today():
               rec.is_next = True 
            else:
               rec.is_next = False
    
    @api.onchange('country_loading_id')
    def erase_country_related(self):
        for rec in self:
            rec.state_loading_id=u''
            rec.city_loading_id=u''
            rec.place_loading_id=u''
            rec.port_loading_id=u''
            rec.terminal_loading_id=u''

    
    @api.onchange('state_loading_id')
    def erase_state_related(self):
        for rec in self:
            rec.city_loading_id=u''
            
    @api.onchange('city_loading_id')
    def erase_city_related(self):
        for rec in self:
            rec.place_loading_id=u''
    
    @api.onchange('port_loading_id')
    def erase_port_related(self):
        for rec in self:
            rec.terminal_loading_id=u''
               
class AirLineCostLine(models.Model):
    _name = 'air.line.cost.line'
    _description = "AirLineCostLine"
    
    commodity_id = fields.Many2one('commodity',String='Commodity',required=True)
    product_id = fields.Many2one('product.product',String='Product',required=True)
    package_id = fields.Many2one('packaging', string='Package Name')
    quantity = fields.Float()
    operation = fields.Char()
    volume = fields.Float()
    chargeable_weight = fields.Char('Chargeable Weight')
    currency_id = fields.Many2one('res.currency', string="Currency")
    cost = fields.Monetary(required=True)
    total = fields.Monetary('Total', compute='_compute_total')
    air_line_cost_id = fields.Many2one('air.line.cost')
    
    @api.depends()
    def _compute_total(self):
        for rec in self:
            if rec.air_line_cost_id.currency_id:
                value = rec.quantity * rec.cost
                
                value  = rec.air_line_cost_id.currency_id._convert(value,rec.air_line_cost_id.currency_id,self.env.user.company_id,fields.Date.today())
                total_add = 0.0
                for i in rec.air_line_cost_id.air_line_add_cost_ds:
                    total_add += i.currency_id._convert(i.cost,rec.air_line_cost_id.currency_id,self.env.user.company_id,fields.Date.today())
                    
                rec.total = total_add + value
                
class AirlineAdditCost(models.Model):
    _name='air.line.addit.cost'
    _description='AirlineAdditCost'
     
    product_id = fields.Many2one('product.product', string='Product', required=True ,domain=[('is_add_cost', '=', True)])
    currency_id = fields.Many2one('res.currency', string="Currency",required=True)
    cost = fields.Monetary(required=True)
    air_line_costt_id = fields.Many2one('air.line.cost')
     
class AirLineNote(models.Model):
    _name='air.line.note'
    _description='AirLineNote'
    
    note=fields.Text('note')
    air_line_costt_id = fields.Many2one('air.line.cost')
    
    
    
    
    
    
    
    
    
    
    
    
    