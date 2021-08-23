# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError
from odoo.osv.expression import AND , OR
from pydoc import doc


class InquiryAdditionalCost(models.Model):
    _name = 'inquiry.additional.cost'
    _description = "InquiryAdditionalCost"
    
    product_id = fields.Many2one('product.product', string='Name', required=True)
    cost = fields.Float(required=True)
    inquiry_id = fields.Many2one('sale.inquiry')
    job_id = fields.Many2one('job')


class SaleInquiryCondition(models.Model):
    _name = 'sale.inquiry.condition'
    _description = "SaleInquiryCondition"
    
    name = fields.Char(required=True)
    inquiry_id = fields.Many2one('sale.inquiry', ondelete='cascade')
    job_id = fields.Many2one('job', ondelete='cascade')
    job_one_id = fields.Many2one('job', ondelete='cascade')

    
class SaleInquiryContainer(models.Model):
    _name = 'sale.inquiry.container'
    _description = "SaleInquiryContainer"
    
    line_cost_line_id = fields.Many2one('line.cost.line', string="Container", required=True)
    container_id = fields.Many2one('container.size',related="line_cost_line_id.sea_lines_id.container_size_id")
    transport_line_id = fields.Many2one('transport.price.line')
    truck_type_id = fields.Many2one('truck.type',related="transport_line_id.truck_type_id",readonly=True)
    weight_type_id = fields.Many2one('weight.type',related="transport_line_id.weight_type_id",readonly=True)
    container_qty = fields.Integer(required=True)
    target_rate = fields.Float()
    sold = fields.Float()
    first_rate = fields.Float()
    second_rate = fields.Float()
    third_rate = fields.Float()
    inquiry_id = fields.Many2one('sale.inquiry')
    job_id = fields.Many2one('job')
    driver_info_id = fields.Many2one('driver.info')
    shipment_type = fields.Selection([('cross', 'Cross'), ('import', 'Import'), ('export', 'Export')], related="inquiry_id.shipment_type")
    line_id = fields.Many2one('line.cost', related="inquiry_id.shipping_line_id")
    country_loading_id = fields.Many2one('res.country', related="inquiry_id.country_loading_id")
    port_loading_id = fields.Many2one(string='port', related="inquiry_id.port_loading_id")
    country_dest_id = fields.Many2one('res.country', related="inquiry_id.country_dest_id")
    port_dest_id = fields.Many2one('port', related="inquiry_id.port_dest_id")
    is_loading = fields.Boolean( related="inquiry_id.is_loading")
    is_discharge = fields.Boolean(related="inquiry_id.is_discharge")
    place_loading_id = fields.Many2one('res.place', related="inquiry_id.place_loading_id")
    place_of_port_id = fields.Many2one('res.place',related="inquiry_id.place_of_port_id")
    cost = fields.Float(compute="_compute_cost")
    
    
    
    @api.depends('transport_line_id','container_qty')
    def _compute_cost(self):
        for rec in self:
            rec.cost =  rec.transport_line_id and  (rec.transport_line_id.price * rec.container_qty + sum([0]+[i.cost * rec.container_qty if i.per_quantity else i.cost for i in  rec.transport_line_id.cost_id.cost_line_ids.filtered(lambda x:x.container_size_id.id == rec.container_id.id)])) or 0.0


    
class ClearanceCostLine(models.Model):
    _name = 'inquiry.clearance.cost'
    _description = "ClearanceCostLine"
    
    customs_point_id = fields.Many2one('res.partner', 'Customs Point', required=True)
    customs_dec_id = fields.Many2one('customs.declaration', string="Customs Declaration")
    clearance_id = fields.Many2one('res.partner', 'Clearance Company')
    rate = fields.Float()
    inquiry_id = fields.Many2one('sale.inquiry', ondelete='cascade')
    
    
class SaleInquiryLineShipment(models.Model):
    _name = 'sale.inquiry.line'
    _description = "SaleInquiryLineShipment"
    
    product_id = fields.Many2one('product.product', required=True)
    temperature = fields.Float('Temperature', related="product_id.temperature")
    warehouse_condition = fields.Char('Warehouse condition', related="product_id.warehouse_condition")
    warehouse_condition_att = fields.Binary(attachment=True, string="Attachment Ware", related="product_id.warehouse_condition_att")
    transport_condition = fields.Char('Transport condition', related="product_id.transport_condition")
    transport_condition_att = fields.Binary(attachment=True, string="Attachment Trans", related="product_id.transport_condition_att")
    port_condition = fields.Char('Port condition', related="product_id.port_condition")
    port_condition_att = fields.Binary(attachment=True, string="Attachment Port", related="product_id.port_condition_att")
    other_condition = fields.Char('Other condition', related="product_id.other_condition")
    other_condition_att = fields.Binary(attachment=True, string="Attachment Other", related="product_id.other_condition_att")
    inquiry_id = fields.Many2one('sale.inquiry')
    job_id = fields.Many2one('job')
    


class SaleInquiry(models.Model):
    _name = 'sale.inquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "SaleInquiry"
    
    name = fields.Char(readonly=True)
    from_validity_date = fields.Date()
    to_validity_date = fields.Date()
    partner_id = fields.Many2one('res.partner',required=True)
    order_line_shipment_ids = fields.One2many('sale.inquiry.line', 'inquiry_id')
    release = fields.Boolean('Release')
    admin_release = fields.Boolean('Admin Release')
    sale_state = fields.Selection([('progress', 'In Progress'), ('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed')], default="progress")

#   sales inquiry filters
    shipment_method = fields.Selection([('clearance', 'Clearance'), 
                                        ('sea_freight', 'Sea freight'), 
                                        ('land_freight', 'Land Freight'), 
                                        ('air_freight', 'Air Freight')],string="Shipment Method", store=True)
    shipment_type = fields.Selection([('import', 'Import'), 
                                        ('export', 'Export'), 
                                        ('cross', 'Cross'), 
                                        ('internal', 'internal')],string="Shipment Type",store=True)  
    shipment_logic = fields.Selection([('fcl', 'FCL'), 
                                        ('lcl', 'LCL'), 
                                        ('roro', 'RORO')],string="Shipment logic",store=True)
    customer_ref = fields.Char('Customer Reference')
    shipper_ref = fields.Char('Shipper Reference')
    consignee_ref = fields.Char('Consignee Reference') 
    notify_party_ref = fields.Char('Notify Party Ref') 
    add_notify_ref = fields.Char('Additional Notify Ref') 
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    first_notify_id = fields.Many2one('res.partner', string='First Notify Party')
    add_notify_id = fields.Many2one('res.partner', string='Additional Notify')
#   the condition of shipment delivery
    shiping_terms = fields.Selection([('exw', 'EXW'), 
                                        ('fca', 'FCA'), 
                                        ('cpt', 'CPT'),
                                        ('cip', 'CIP'), 
                                        ('dat', 'DAT'), 
                                        ('dap', 'DAP'),
                                        ('ddp', 'DDP'), 
                                        ('dore_to_dore', 'Door to Door'), 
                                        ('fas', 'FAS'),
                                        ('fob', 'FOB'), 
                                        ('cfr', 'CFR'), 
                                        ('cif', 'CIF'),
                                        ('c_and_f', 'C & F')],string="Shipment Terms",store=True)
#   shipment details fields added 22-05-2019
    volume_ship = fields.Float('Volume')
    dimensions = fields.Float('Dimensions')
    weight = fields.Float('Weight')
    charge_weight = fields.Float('Chargeable Weight')
    type_package_no = fields.Float('No. & Type of Packages')
    
#     shipment_type = fields.Selection([('cross', 'Cross'), ('import', 'Import'), ('export', 'Export')])
    sales_person = fields.Many2one('res.users', default=lambda self: self.env.user)
    user_operation_id = fields.Many2one('res.users')
    customer_class_id = fields.Many2one('customer.class', related="partner_id.customer_class_id", store=True)
    shipper_id = fields.Many2one('res.partner', string='Shipper')
    
    country_loading_id = fields.Many2one('res.country', string="Country Of Loading")
    city_loading_id = fields.Many2one('res.city', string="City Of Loading")
    place_loading_id = fields.Many2one('res.place', string="Place Of Loading")
    port_loading_id = fields.Many2one('port', string="POL")
    state_loading_id = fields.Many2one('res.country.state', string="State Of Loading")
    country_dest_id = fields.Many2one('res.country', string="Country Of Destination")
    city_dest_id = fields.Many2one('res.city', string="City Of Destination")
    place_dest_id = fields.Many2one('res.place', string="Place Of Destination")
    port_dest_id = fields.Many2one('port', string="POD")
    place_of_port_id = fields.Many2one('res.place')
    state_dest_id = fields.Many2one('res.country.state', string="State Of Destination")
    is_loading = fields.Boolean()
    is_discharge = fields.Boolean()
    
    delivery_place_id = fields.Many2one('res.place', string='Place Of Delivery')

    
    agreement_method_id = fields.Many2one('agreement.method')
    customs_dec_id = fields.Many2one('customs.declaration', string="Customs Declaration")
    shipping_line_id = fields.Many2one('line.cost', string="Shipping Line")
    shipping_line_ids = fields.Many2many('line.cost', compute="_shipping_line_ids", string="Shipping Lines")
    partner_shipping_line_id = fields.Many2one('res.partner', related="shipping_line_id.line_id", string="Partner Shipping Line")
    
    free_days = fields.Integer()
    vessel_id = fields.Many2one('vessel')
    voyage_id = fields.Many2one('voyages.detail')
    etd_date = fields.Date('ETD Date', related="voyage_id.etd_date", readonly=True)
    eta_date = fields.Date('ETA Date', related="voyage_id.eta_date", readonly=True)
    
    c_month = fields.Char('Month', default=datetime.date.today().month, readonly=True)
    c_year = fields.Char('Year', default=datetime.date.today().year, readonly=True)
    condition_ids = fields.One2many('sale.inquiry.condition', 'inquiry_id', 'Conditions')
    container_size_ids = fields.One2many('sale.inquiry.container', 'inquiry_id', 'Container Price')
    container_ids = fields.Many2many('container.size', compute="_compute_container_ids")
    
    
    state = fields.Selection([('New', 'New'),('Progress', 'Progress'), ('Confirmed', 'Confirmed'), 
                              ('Cancelled', 'Cancelled'),
                              ('Job', 'Job')], default="New")
    stage = fields.Selection([('New', 'New'),('Progress', 'Progress'), ('Confirmed', 'Confirmed'), 
                              ('Cancelled', 'Cancelled'),
                              ('Job', 'Job')], default="New")

    sea_rate = fields.Float('Sea Rate #######')
    insurance_cost_id = fields.Many2one('insurance.cost', 'Insurance Cost') 
    insurance_cost_ids = fields.Many2many('insurance.cost', compute="_insurance_cost_ids", string="Insurance Costs")
    insurance_rate = fields.Monetary(related="insurance_cost_id.total",readonly=True)
    transport_rate = fields.Float(compute='_compute_transport_rate')
    clearance_id = fields.Many2one('clearance.cost','Clearance')
    clearance_cost_ids = fields.One2many('sale.clearance.cost.line', 'inquiry_id', 'Clearance Cost',readonly=True)
    additional_cost_ids = fields.One2many('inquiry.additional.cost', 'inquiry_id', 'Additional Cost')

#   Transport details  
    transporter_cost_id = fields.Many2one('transport.cost', string='Transport')
    transporter_free_days = fields.Integer(related='transporter_cost_id.free_days', string='Transport Free Days')
#     transporter_name = fields.Char(related='transporter_cost_id.partner_id', string='Transporter name')
    transporter_total = fields.Monetary(related='transporter_cost_id.total', string='Transport Total')
    currency_id = fields.Many2one('res.currency', related="transporter_cost_id.currency_id" ,string="Currency")
#   Commodity key
    commodity_ids = fields.Many2many('commodity') 
    commodity_domain_ids = fields.Many2many('commodity', related='partner_id.commodity_ids') 
    issue_bill_lading_to = fields.Many2one ('res.partner', string='Issue Bill of lading To')
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms",
                                      related='partner_id.property_payment_term_id')
    air_line_id = fields.Many2one('air.line.cost', string='AirLine', domain=[('is_expired','!=',True)])
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms", 
                                      related='air_line_id.payment_term_id')
    air_line_cost_line_ds =fields.One2many('air.line.cost.line','air_line_cost_id' ,related='air_line_id.air_line_cost_line_ds')
    
#     @api.multi
#     def action_send_email(self):
#         for rec in self:
#             rec.ensure_one()
#             template = rec.env.ref('base_enh.send_email_sale_inquiry')
#             rec.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
    
#   loaded country related
    @api.onchange('country_loading_id')
    def erase_related_addr(self):
        self.state_loading_id = u''
        self.city_loading_id= u''
        self.place_loading_id = u''
        self.port_loading_id = u''
        self.place_of_port_id = u''
       
    
    @api.onchange('state_loading_id')
    def erase_related_addr_three(self):
        self.city_loading_id= u''
        self.place_loading_id = u''

    @api.onchange('city_loading_id')
    def erase_related_addr_four(self): 
        self.place_loading_id = u''
        
    @api.onchange('port_loading_id')
    def erase_related_addr_six(self): 
        self.place_of_port_id = u''
       
#   country destination related   
    @api.onchange('country_dest_id')
    def erase_related_addr_seven(self):
        self.state_dest_id = u''
        self.city_dest_id= u''
        self.place_dest_id = u''
        self.port_dest_id = u''
        self.delivery_place_id = u''
        
    @api.onchange('state_dest_id')
    def erase_related_addr_eight(self):
        self.city_dest_id= u''
        self.place_dest_id = u''

        
    @api.onchange('city_dest_id')
    def erase_related_addr_nign(self):
        self.place_dest_id = u''

    @api.onchange('port_dest_id')
    def erase_related_addr_eleven(self):
        self.delivery_place_id = u''

    @api.onchange('partner_id')
    def partner_onchange(self):
        """ erase customer reference if customer 'Partner' field is empty"""
        for rec in self:
            rec.customer_ref=u''
            rec.commodity_ids=u''
        
    
    @api.onchange('shipper_id')
    def shipper_onchange(self):
        """ erase shipper reference if 'Shipper' field is empty"""
        self.shipper_ref=u''
    
    @api.onchange('consignee_id')
    def consignee_onchange(self):
        """ erase consignee reference if 'Consignee' field is empty"""
        self.consignee_ref=u''        
    
    @api.onchange('first_notify_id')
    def first_notify_onchange(self):
        """ erase notify reference if 'Notify Party' field is empty"""
        self.notify_party_ref=u''
        
    @api.onchange('add_notify_id')
    def add_nofity_onchange(self):
        """ erase additional notify reference if 'Additional Notify Party' field is empty"""
        self.add_notify_ref=u''
        
        
        
    
    @api.depends('container_size_ids','container_size_ids.cost')
    def _compute_transport_rate(self):
        for rec in self:
            rec.transport_rate = sum([0]+rec.container_size_ids.mapped('cost'))
    @api.depends('container_size_ids','container_size_ids.line_cost_line_id')
    def _compute_container_ids(self):
        for rec in self:
            rec.container_ids = [(6,0,rec.container_size_ids.mapped('line_cost_line_id.sea_lines_id.container_size_id.id'))]
            
    @api.onchange('clearance_id','container_size_ids','container_size_ids.line_cost_line_id','container_size_ids.container_qty')
    def _compute_clearance_cost_ids(self):
        for rec in self:
            cci_obj = self.env['sale.clearance.cost.line']
            rec.clearance_cost_ids.unlink()
            if rec.clearance_id:
                for i in rec.container_size_ids:
                    total = 0.0
                    qty = i.container_qty
                    for l in rec.clearance_id.cost_line_ids:
                        if qty <= 0:
                            break
                        c_qty = l.to_truck - l.from_truck  +1
                        c_qty = c_qty if c_qty < qty else qty
                        qty -= c_qty
                        total += l.cost * c_qty
                    rec.clearance_cost_ids = [(0,0,{'container_id':i.line_cost_line_id.sea_lines_id.container_size_id.id,'cost':total,'inquiry_id':rec.id})]
                        
    @api.depends('country_loading_id','country_dest_id',
                 'city_loading_id','state_loading_id',
                 'city_dest_id','state_dest_id',)
    def _insurance_cost_ids(self):
       insurance_obj = self.env['insurance.cost']
       for rec in self:
            domain = [  ('country_loading_id', '=', rec.country_loading_id.id),
                        ('country_dest_id', '=', rec.country_dest_id.id),
                        ('is_expired','!=',True)
                        ]
            domain = AND([domain, OR([[('city_loading_id', '=', rec.city_loading_id.id),
                                      ('city_dest_id', '=', rec.city_dest_id.id)],
                                    [('state_loading_id', '=', rec.state_loading_id.id),
                                      ('state_dest_id', '=', rec.state_dest_id.id)]])])
           
            insurance_cost_ids = insurance_obj.search(domain)
            rec.insurance_cost_ids = [(6,0,insurance_cost_ids.ids)]
            
            
    
    @api.depends('order_line_shipment_ids',
                 'order_line_shipment_ids.product_id',
                 'country_loading_id','port_dest_id',
                 'port_loading_id','country_dest_id',
                 'shipment_type','partner_id',
                 'is_loading','city_loading_id',
                 'place_loading_id','state_loading_id',
                 'city_dest_id','place_dest_id',
                 'state_dest_id','is_discharge')
    def _shipping_line_ids(self):
       line_cost_obj = self.env['line.cost']
       for rec in self:
            commodity_ids = rec.commodity_ids
            domain = [  ('country_loading_id', '=', rec.country_loading_id.id),
                        ('port_loading_id', '=', rec.port_loading_id.id),
                        ('port_dest_id', '=', rec.port_dest_id.id),
                        ('country_dest_id', '=', rec.country_dest_id.id),
                        ('line_cost_ids.sea_lines_id.type', '=', rec.shipment_type),
                        ('is_expired', '=', False)]
            domain = AND([domain, OR([[('customer_id', '=', rec.partner_id.id)],[('customer_id', '=', False)]])])
           
            domain = AND([domain, OR([[('commodity_id', 'in', commodity_ids.ids)],[('fak', '=', True)]])])         
                        
            if rec.is_loading:
                domain = AND([domain,
                                AND([
                                    [('line_cost_ids.is_loading', '=', True),('place_loading_id', '=', rec.place_loading_id.id)],
                                    OR([[('city_loading_id', '=', rec.city_loading_id.id)],[('state_loading_id', '=', rec.state_loading_id.id)]])
                                    ])
                            ])
            if rec.is_discharge:
                domain = AND([domain,
                                AND([
                                    [('line_cost_ids.is_discharge', '=', True),('place_dest_id', '=', rec.place_dest_id.id)],
                                    OR([[('city_dest_id', '=', rec.city_dest_id.id)],[('state_dest_id', '=', rec.state_dest_id.id)]])
                                    ])
                            ])
            line_cost_ids = line_cost_obj.search(domain)
            rec.shipping_line_ids = [(6,0,line_cost_ids.ids)]
           
          
    @api.constrains('from_validity_date', 'to_validity_date')
    def validity_date_constraint(self):
        for rec in self:
            if rec.from_validity_date and rec.to_validity_date and rec.from_validity_date > rec.to_validity_date:  
                raise UserError("""The 'From Validity Date' must be less than 'To Validity Date'.""")
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('inquiry.seq')
        return super(SaleInquiry, self).create(vals_list)
    
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
            'domain': [('sale_inquiry_id.id', '=', self.id),('user_operation_id.id','=', self._uid)], 
            'target': 'current',  
               } 
    
    @api.multi  
    def call_sale(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('sale_order', 'view_order_tree')[1]
            form_res = mod_obj.get_object_reference('sale_order', 'view_order_form')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('sale.order.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'sale.order',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form')], 
            'domain': [('partner_id.id','=',self.partner_id.id),('state','=',"sale")], 
            'target': 'current',  
               } 
    @api.multi  
    def call_purchase(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
            form_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('purchase.order.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'purchase.order',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form')], 
            'domain': [('partner_id.id','=',self.partner_id.id),('state','=',"purchase")], 
            'target': 'current',  
               } 
    @api.multi  
    def call_invoice(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('account_invoice', 'invoice_tree')[1]
            form_res = mod_obj.get_object_reference('account_invoice', 'invoice_form')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('account.invoice.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'account.invoice',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form')], 
            'domain': [('partner_id.id','=',self.partner_id.id)], 
            'target': 'current',  
               }
  

    @api.multi
    def approve_sale_mgr(self):
        """sales manager approval button  """
        self.write({'state': 'Progress','stage': 'Progress'})
    
    @api.multi
    def approve_acct_mgr(self):
        """accounting manager approval button  """
        self.write({'state': 'Confirmed','stage': 'Confirmed'})
        
    @api.multi
    def approve_gm(self):
        """general manager approval and create job button  """
        for rec in self:
            if not rec.user_operation_id:
                raise UserError("Please select operation to handle the job")
            else:
                rec.write({'state': 'Job','stage': 'Job'})
                job_obj = self.env['job']
                rec.ensure_one()
                job_obj.create({'sale_inquiry_id':self.id})
            
        
    
    @api.multi
    def cancel_gm(self):
        """general manager cancel sale inquiry button  """
        self.write({'state': 'Cancelled','stage': 'Cancelled'})
    
    @api.multi
    def set_new_gm(self):
        """general manager set sale inquiry button  """
        self.write({'state': 'New','stage': 'New'})

                   
class SaleClearanceCostLine(models.Model):
    _name = 'sale.clearance.cost.line'
    _description = "SaleClearanceCostLine"
    
    container_id = fields.Many2one('container.size')
    cost = fields.Float()
    inquiry_id = fields.Many2one('sale.inquiry',ondelete="cascade")
    job_id = fields.Many2one('job',ondelete="cascade")
   
    
  
        
