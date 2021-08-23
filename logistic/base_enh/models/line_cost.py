# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AdditionalCost(models.Model):
    _name = 'additional.cost'
    _description = "AdditionalCost"
    
    product_id = fields.Many2one('product.product', string='Additional Name', required=True ,domain=[('is_add_cost', '=', True)])
    cost = fields.Monetary(required=True)
    line_cost_id = fields.Many2one('line.cost' ,required=True)
    currency_id = fields.Many2one('res.currency', string="Currency",required=True)
    
    @api.constrains('cost')
    def check_cost_value(self):
        """cost value greater than 0"""
        for rec in self:
            if rec.cost == 0 or rec.cost < 0:
                raise UserError("'Cost' value should be greater than 0")
    
#     _sql_constraints = [('check_additional_cost_cost', 'CHECK(cost > 0)', 'The additional cost must be greater than zero.')]
    
    
class LineCostLine(models.Model):
    _name = 'line.cost.line'
    _rec_name = "sea_lines_id"
    _description = "LineCostLine"
    
    sea_lines_id = fields.Many2one('sea.lines', 'Container', required=True)
    partner_id = fields.Many2one('res.partner',related="line_cost_id.line_id")
    min_qty = fields.Integer('Minimum Quantity', required=True)
    agency = fields.Monetary('Agency', compute="_compute_agency",store=True)
    transport_loading_price = fields.Monetary()
    transport_discharge_price = fields.Monetary()
    insurance_price = fields.Monetary()
    clearance_price = fields.Monetary()
    is_loading = fields.Boolean(compute='_compute_is_loading',store=True)
    is_discharge = fields.Boolean(compute='_compute_is_discharge',store=True)
    is_clearance_cost = fields.Boolean()
    is_insurance_cost = fields.Boolean()
    type = fields.Selection([('loading','Loading'),('discharg','Discharg')])
    product_id = fields.Many2one('product.product', string='Name Of Discount', domain=[('is_discount', '=', True)])
    value = fields.Monetary('Discount Value')
    rate = fields.Monetary('Rate')
    line_cost_id = fields.Many2one('line.cost', required=True)
    total = fields.Monetary('Total',compute='_compute_total')
    currency_id = fields.Many2one('res.currency', string="Currency",required=True)
    line_type = fields.Selection(related="line_cost_id.type", string='Line Cost Type')
    transport_loading_id = fields.Many2one('transport.type',related="line_cost_id.transport_loading_id")
    transport_dest_id = fields.Many2one('transport.type',related="line_cost_id.transport_dest_id")
    
    @api.depends('sea_lines_id','currency_id')
    def _compute_agency(self):
        for rec in self:
            if rec.sea_lines_id:
                rec.agency = self.env.user.company_id.currency_id._convert(rec.sea_lines_id.agency,rec.currency_id,self.env.user.company_id,fields.Date.today())
            else:
                rec.agency = 0
    @api.multi
    @api.depends('transport_loading_id')
    def _compute_is_loading(self):
        for rec in self:
            print(rec.line_cost_id.transport_loading_id)
            rec.is_loading = bool(rec.transport_loading_id)
            
    
    @api.multi
    @api.depends('transport_dest_id')
    def _compute_is_discharge(self):
        for rec in self:
            rec.is_loading = bool(rec.transport_dest_id)  
        
    @api.depends()
    def _compute_total(self):
        for rec in self:
            if rec.line_cost_id.currency_id:
                value = rec.clearance_price + rec.insurance_price + rec.agency + rec.rate+ rec.transport_discharge_price + rec.transport_loading_price - rec.value
                
                value  = rec.line_cost_id.currency_id._convert(value,rec.line_cost_id.currency_id,self.env.user.company_id,fields.Date.today())
                total_add = 0.0
                for i in rec.line_cost_id.additional_cost_ids:
                    total_add += i.currency_id._convert(i.cost,rec.line_cost_id.currency_id,self.env.user.company_id,fields.Date.today())
                    
                rec.total = total_add + value + rec.line_cost_id.bill_fees - rec.line_cost_id.discount
            
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        return super(LineCostLine, self)._search( args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.onchange('product_id') 
    def erase_value_discount(self):
        """Erase discount value if product name changed"""
        for rec in self:
            rec.value=False

class LineCostNote(models.Model):
    _name='line.cost.note' 
    _description='line cost note table'
    
    note=fields.Text()
    cost_id=fields.Many2one('line.cost')

class LineCost(models.Model):
    _name = 'line.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'line_id'
    _description = "LineCost"
    
    line_id = fields.Many2one('res.partner', string="Shipping Line", required=True,domain=[('company_type', '=', 'company'),('is_sea_line', '=', True)])
    quot_number = fields.Char(string="Quotation Number", required=True)
    date = fields.Date('Date', required=True)
    country_loading_id = fields.Many2one('res.country', string="Country Of Loading", required=True)
    state_loading_id = fields.Many2one('res.country.state', string="State Of Loading")
    city_loading_id = fields.Many2one('res.city', string="City Of Loading")
    place_loading_id = fields.Many2one('res.place', string="Place Of Loading", required=False)
    transport_loading_id = fields.Many2one('transport.type', string="Transport Type Of Loading")
    port_loading_id = fields.Many2one('port', string="POL", required=True)
    terminal_loading_id = fields.Many2one('res.place', string="Terminal of Loading", required=True)
    place_dest_id = fields.Many2one('res.place', string="Place Of Destination")
    
    is_same_country = fields.Boolean('Is Same Country', default=True)
    country_dest_id = fields.Many2one('res.country', string="Country Of Discharge", required=True)
    state_dest_id = fields.Many2one('res.country.state', string="State Of Discharge")
    city_dest_id = fields.Many2one('res.city', string="City Of Discharge")
    terminal_des_same_id = fields.Many2one('res.place', string="Terminal of Discharge")
    
    country_diff_dest_id = fields.Many2one('res.country', string="Country Of Last Destination")
    state_diff_dest_id = fields.Many2one('res.country.state', string="State Of Last Destination")
    city_diff_dest_id = fields.Many2one('res.city', string="City Of Last Destination")
    place_diff_dest_id = fields.Many2one('res.place', string="Place Of Last Destination")
    delivery_diff_place_id = fields.Many2one('res.place', 'Place Of Last Delivery')
    
    port_dest_id = fields.Many2one('port', string="POD", required=True)
    transport_dest_id = fields.Many2one('transport.type', string="Transport Type Of Discharge")
    delivery_place_id = fields.Many2one('res.place', 'Place Of Delivery')
    bill_fees = fields.Monetary('Bill fees',compute='_compute_bill_fees',store=True)
    free_demurrage_and_detention = fields.Integer()
    transt_time = fields.Integer(required=True)
    customer_id = fields.Many2one('res.partner',stirng='Named Account')
    fak = fields.Boolean('FAK',default=True)
    product_id = fields.Many2one('product.product')
    commodity_id = fields.Many2many('commodity')
    commodity_domain_ids = fields.Many2many('commodity', related='customer_id.commodity_ids')
    start_date = fields.Date('Start Date')
    expiry_date = fields.Date('Expiry Date')
    note = fields.Text('Notes')
    is_expired = fields.Boolean(compute='_compute_is_expired',search="_search_is_expired")
    is_next = fields.Boolean(compute='_compute_is_next',search="_search_is_next")
    line_cost_ids = fields.One2many('line.cost.line','line_cost_id',string="Price")
    additional_cost_ids = fields.One2many('additional.cost','line_cost_id',string="Additional Cost")
    product_discount_id = fields.Many2one('product.product', string='Additional Discount' ,domain=[('is_discount', '=', True)])
    discount = fields.Monetary(default=0.0)
    active=fields.Boolean(default=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    type = fields.Selection([('import','Import'),('export','Export'),('cross','Cross')],compute="_compute_type")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms", 
                                      related='line_id.property_supplier_payment_term_id')
    line_cost_note_ids=fields.One2many('line.cost.note','cost_id')
    
    @api.onchange('customer_id')
    def erase_customer_related(self):
        for rec in self:
            rec.commodity_id=u''
            
    
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
            'domain': [('shipping_line_id.id', '=', self.id)], 
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
            'domain': [('shipping_line_id.id', '=', self.id)], 
            'target': 'current',  
               }
     
    @api.onchange('place_des_id')
    def erase_related_data_loading(self):
        """erase data of Transport type, country related, and fees"""
        for rec in self:
            rec.transport_des_id=u''
            rec.delivery_place_id=u''
            rec.bill_fees=u''
            rec.currency_id=u''
            rec.transt_time=u''
            rec.start_date=u''
            rec.expiry_date=u''
            rec.country_diff_dest_id=u''
            
    @api.multi
    @api.onchange('transport_loading_id')
    def clear_trans_load_pri(self):
        """clear data of transport loading price once transport type of loading changed"""
        for rec in self:
            n = rec.line_cost_ids
            for l in n:
                l.transport_loading_price =u''
            
    
    @api.multi
    @api.onchange('transport_dest_id')
    def clear_trans_discharge_pri(self):
        """clear data of transport discharge price once transport type of delivery changed"""
        for rec in self:
            n = rec.line_cost_ids
            for k in n:
                k.transport_discharge_price=u''
    
    @api.multi
    @api.onchange('is_same_country')
    def erase_last_des_related(self):
        for rec in self:
            if rec.is_same_country == True:
                rec.country_diff_dest_id = u''
                rec.state_diff_dest_id = u''
                rec.city_diff_dest_id = u''
                rec.place_diff_dest_id = u''
                rec.delivery_diff_place_id = u''
    @api.multi
    @api.depends('country_diff_dest_id','country_dest_id','country_loading_id')
    def _compute_type(self):
        my_country = self.env.user.company_id.country_id.id
        for rec in self:
            if my_country in rec.country_diff_dest_id.ids or my_country in rec.country_dest_id.ids:
                rec.type = "import"
            elif my_country in rec.country_loading_id.ids:
                rec.type = "export"
            else:
                rec.type = "cross"
        

        
    
    
    @api.multi
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        for rec in self:
            if rec.expiry_date and rec.expiry_date < fields.Date.today():
               rec.is_expired = True 
            else:
               rec.is_expired = False
               
    @api.multi
    @api.depends('start_date')
    def _compute_is_next(self):
        for rec in self:
            if rec.start_date and rec.start_date > fields.Date.today():
               rec.is_next = True 
            else:
               rec.is_next = False
               
               
    def _search_is_expired(self,op,val):
        sql = """
select id from line_cost where expiry_date <= '%s'
"""%fields.Date.today()
        self._cr.execute(sql)
        ids = self._cr.fetchall()
        ids = [id[0] for id in ids]
        if val and op == '=' or not val and op == '!=':
            domain = [('id','in', ids)]
        else :
            domain = [('id','not in', ids)]
        return domain
    
    def _search_is_next(self,op,val):
        sql = """
select id from line_cost where start_date > '%s'
"""%fields.Date.today()
        self._cr.execute(sql)
        ids = self._cr.fetchall()
        ids = [id[0] for id in ids]
        if val and op == '=' or not val and op == '!=':
            domain = [('id','in', ids)]
        else :
            domain = [('id','not in', ids)]
        return domain
    
    @api.onchange('fak')
    def _onchange_fak(self):
        self.commodity_id = False
        
    @api.onchange('place_loading_id')
    def place_loading_id_related(self):
        for rec in self:
            rec.transt_time=u''
            rec.start_date=u''
            rec.expiry_date=u''
            rec.transport_loading_id=u''
            rec.country_diff_dest_id=u''
         
    #   loaded country related
    @api.onchange('country_loading_id')
    def erase_related_addr(self):
        self.state_loading_id = False
        self.city_loading_id= False
        self.place_loading_id = False
        self.port_loading_id = False
        self.terminal_loading_id = False
    
    @api.onchange('state_loading_id')
    def erase_related_addr_three(self):
        self.city_loading_id= False
        self.place_loading_id = False
    
    @api.onchange('city_loading_id')
    def erase_related_addr_four(self): 
        self.place_loading_id = False
        
    @api.onchange('port_loading_id')
    def erase_related_addr_six(self): 
        self.terminal_loading_id = False
    
#   Destination country related
    @api.onchange('country_dest_id')
    def erase_related_addr_des(self):
        self.state_dest_id = False
        self.city_dest_id= False
        self.place_dest_id = False
        self.port_dest_id = False
        self.terminal_des_same_id = False
        self.delivery_place_id = False
    
    @api.onchange('place_dest_id')
    def place_dest_id_related(self):
        for rec in self:
            rec.transport_dest_id=u''
            rec.customer_id=u''
            rec.start_date=u''
            rec.expiry_date=u''
            rec.country_diff_dest_id=u''
    
    @api.onchange('state_dest_id')
    def erase_related_addr_three_des(self):
        self.city_dest_id= False
        self.place_dest_id = False
    
    @api.onchange('city_dest_id')
    def erase_related_addr_four_des(self): 
        self.place_dest_id = False
        
    @api.onchange('port_dest_id')
    def erase_related_addr_six_des(self): 
        self.terminal_des_same_id = False  
    
    #   Last country related
    @api.onchange('country_diff_dest_id')
    def erase_related_addr_last(self):
        self.state_diff_dest_id = False
        self.city_diff_dest_id= False
        self.place_diff_dest_id = False
        self.port_diff_id = False
        self.terminal_des_diff_id = False
        self.delivery_diff_place_id = False
    
    @api.onchange('state_diff_dest_id')
    def erase_related_addr_three_last(self):
        self.city_diff_dest_id= False
        self.place_diff_dest_id = False
    
    @api.onchange('city_diff_dest_id')
    def erase_related_addr_four_last(self): 
        self.place_diff_dest_id = False
        
    @api.onchange('port_diff_id')
    def erase_related_addr_six_last(self): 
        self.terminal_des_diff_id = False  
    
   
               
   
    @api.constrains('expiry_date','start_date')
    def _expired_date(self):
        for rec in self:
            if rec.expiry_date < rec.start_date:
               raise UserError("'Expiry date' should be greater than 'Start date'")
           
    @api.constrains('transt_time')
    def _transit_time(self):
        for rec in self:
            if rec.transt_time <= 0:
               raise UserError("Transit time should be more than Zero!")

    @api.constrains('discount')
    def discount_value(self):
        for rec in self:
            if rec.discount < 0:
                raise UserError(" 'Discount' value should be greater than or equal zero.")
    
    @api.onchange('product_discount_id')
    def erase_discount_value(self):
        for rec in self:
            rec.discount=False
                
    
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        res = super(LineCost, self).create( vals_list)
        for rec in res:
            if not rec.place_dest_id:
                rec.line_cost_ids.write({'is_discharge':False,'transport_discharge_price':0.0})
            if not rec.place_loading_id:
                rec.line_cost_ids.write({'is_loading':False,'transport_loading_price':0.0})
        return res
    
    @api.multi
    def write(self, vals):
        res = super(LineCost, self).write(vals)
        for rec in self:
            if not rec.place_dest_id:
                rec.line_cost_ids.write({'is_discharge':False,'transport_discharge_price':0.0})
            if not rec.place_loading_id:
                rec.line_cost_ids.write({'is_loading':False,'transport_loading_price':0.0})
        return res
    @api.depends('line_id','currency_id')
    def _compute_bill_fees(self):
        for rec in self:
            if rec.line_id:
                rec.bill_fees  = self.env.user.company_id.currency_id._convert(rec.line_id.bill_fees,rec.currency_id,self.env.user.company_id,fields.Date.today())
            else:
                rec.bill_fees = 0.0
#     @api.multi            
#     @api.onchange('additional_cost_ids','additional_cost_ids.cost','discount')
#     def _compute_total_line_cost(self):
#         """Discount all totals + line cost total - discount"""
#         for rec in self:
#             f=rec.line_cost_ids
#             for i in f:
#                 f.total = f.total + sum(rec.additional_cost_ids.mapped('cost')+[0]) - rec.discount
    
#     @api.depends('price','cost_line_ids','cost_line_ids.cost')
#     def _compute_total(self):
#         for rec in self:
#             rec.total = rec.price + sum(rec.cost_line_ids.mapped('cost')+[0])
            
                   
            
    @api.onchange('line_id')     
    def onchange_line_id(self):
        self.line_cost_ids = [(6,0,[])]
        self.quot_number = False
        self.date = False
        self.cost_line_ids = False
        self.condition_ids = False
    
    
    
    
    
    
