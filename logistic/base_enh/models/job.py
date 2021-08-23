# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError
from odoo.osv.expression import AND , OR

class JobCommodityLine(models.Model):
    _name = 'job.commodity.line'
    _description = "JobCommodityLine"
    
    commodity_id = fields.Many2one('commodity',String='Commodity',required=True)
    package_name = fields.Char()
    quantity = fields.Float()
    operation = fields.Char()
    volume = fields.Float()
    gross_weight = fields.Char()
    job_id = fields.Many2one('job')
    job_one_id = fields.Many2one('job')
    
    

class Job(models.Model):
    _name = 'job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Job"
    
    name = fields.Char(readonly=True)
    sale_inquiry_id = fields.Many2one('sale.inquiry',store=True)
    from_validity_date = fields.Date(related='sale_inquiry_id.from_validity_date')
    to_validity_date = fields.Date(related='sale_inquiry_id.to_validity_date')
    partner_id = fields.Many2one('res.partner', related="sale_inquiry_id.partner_id")
    
    order_line_shipment_ids = fields.One2many('sale.inquiry.line', 
                                              inverse_name='job_id',
                                              related='sale_inquiry_id.order_line_shipment_ids')
    
    release = fields.Boolean(related='sale_inquiry_id.release',string='Release')
    admin_release = fields.Boolean(related='sale_inquiry_id.admin_release',string='Admin Release')
    sale_state = fields.Selection([('progress', 'In Progress'), 
                                   ('confirmed', 'Confirmed'), 
                                   ('not_confirmed', 'Not Confirmed')],
                                    related='sale_inquiry_id.sale_state')
    
    operation_type = fields.Selection([('house', 'House'), 
                                   ('master', 'Master'), 
                                   ('direct', 'Direct'),
                                   ('other', 'Other')],
                                    string='Operation Type')
    
    service = fields.Selection([('door_to_door', 'Door To Door'), 
                                   ('door_to_port', 'Door To Port'), 
                                   ('port_to_port', 'Port To Port'),
                                   ('port_to_door', 'Port To Door')],
                                    string='Service')
    intercom = fields.Char ('Intercom (CR)')

#   sales inquiry filters
    shipment_method = fields.Selection([('clearance', 'Clearance'), 
                                        ('sea_freight', 'Sea freight'), 
                                        ('land_freight', 'Land Freight'), 
                                        ('air_freight', 'Air Freight')],
                                        string="Shipment Method",
                                        related='sale_inquiry_id.shipment_method')
    shipment_type = fields.Selection([('import', 'Import'), 
                                        ('export', 'Export'), 
                                        ('cross', 'Cross'), 
                                        ('internal', 'internal')],string="Shipment Type",
                                        related='sale_inquiry_id.shipment_type')  
    shipment_logic = fields.Selection([('fcl', 'FCL'), 
                                        ('lcl', 'LCL'), 
                                        ('roro', 'RORO')],string="Shipment logic",
                                        related='sale_inquiry_id.shipment_logic')
    customer_ref = fields.Char(string='Customer Reference',related='sale_inquiry_id.customer_ref')
    shipper_ref = fields.Char(string='Shipper Reference',related='sale_inquiry_id.shipper_ref')
    consignee_ref = fields.Char(string='Consignee Reference',related='sale_inquiry_id.consignee_ref') 
    notify_party_ref = fields.Char(string='Notify Party Ref',related='sale_inquiry_id.notify_party_ref') 
    add_notify_ref = fields.Char(string='Additional Notify Ref') 
    consignee_id = fields.Many2one('res.partner', string='Consignee',related="sale_inquiry_id.consignee_id")
    first_notify_id = fields.Many2one('res.partner', string='First Notify Party',
                                      related="sale_inquiry_id.first_notify_id")
    add_notify_id = fields.Many2one('res.partner', string='Additional Notify',
                                    related="sale_inquiry_id.add_notify_id")
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
                                        ('c_and_f', 'C & F')],string="Shipment Terms",store=True,
                                        related='sale_inquiry_id.shiping_terms')
#   shipment details fields added 22-05-2019
    volume_ship = fields.Float(related='sale_inquiry_id.volume_ship',string='Volume')
    dimensions = fields.Float(related='sale_inquiry_id.dimensions',string='Dimensions')
    weight = fields.Float(related='sale_inquiry_id.weight',string='Weight')
    charge_weight = fields.Float(related='sale_inquiry_id.charge_weight',string='Chargeable Weight')
    type_package_no = fields.Float(related='sale_inquiry_id.type_package_no',string='No. & Type of Packages')
    
#     shipment_type = fields.Selection([('cross', 'Cross'), ('import', 'Import'), ('export', 'Export')])
    sales_person = fields.Many2one('res.users', related="sale_inquiry_id.sales_person")
    user_operation_id = fields.Many2one('res.users',related="sale_inquiry_id.user_operation_id")
    customer_class_id = fields.Many2one('customer.class', related="sale_inquiry_id.customer_class_id"
                                        , store=True)
    shipper_id = fields.Many2one('res.partner', string='Shipper',
                                  related="sale_inquiry_id.shipper_id")
    
    country_loading_id = fields.Many2one('res.country', string="Country Of Loading",
                                         related="sale_inquiry_id.country_loading_id")
    city_loading_id = fields.Many2one('res.city', string="City Of Loading",
                                      related="sale_inquiry_id.city_loading_id")
    place_loading_id = fields.Many2one('res.place', string="Place Of Loading",
                                       related="sale_inquiry_id.place_loading_id")
    port_loading_id = fields.Many2one('port', string="POL",
                                      related="sale_inquiry_id.port_loading_id")
    state_loading_id = fields.Many2one('res.country.state', string="State Of Loading",
                                       related="sale_inquiry_id.state_loading_id")
    country_dest_id = fields.Many2one('res.country', string="Country Of Destination",
                                      related="sale_inquiry_id.country_dest_id")
    city_dest_id = fields.Many2one('res.city', string="City Of Destination",
                                   related="sale_inquiry_id.city_dest_id")
    place_dest_id = fields.Many2one('res.place', string="Place Of Destination",
                                    related="sale_inquiry_id.place_dest_id")
    port_dest_id = fields.Many2one('port', string="POD",related="sale_inquiry_id.port_dest_id")
    place_of_port_id = fields.Many2one('res.place',related="sale_inquiry_id.place_of_port_id")
    state_dest_id = fields.Many2one('res.country.state', string="State Of Destination"
                                    ,related="sale_inquiry_id.state_dest_id")
    is_loading = fields.Boolean(related='sale_inquiry_id.is_loading')
    is_discharge = fields.Boolean(related='sale_inquiry_id.is_discharge')
    
    delivery_place_id = fields.Many2one('res.place', string='Place Of Delivery',
                                        related="sale_inquiry_id.delivery_place_id")

    
    agreement_method_id = fields.Many2one('agreement.method', related="sale_inquiry_id.agreement_method_id")
    customs_dec_id = fields.Many2one('customs.declaration', string="Customs Declaration",
                                     related="sale_inquiry_id.customs_dec_id")
    shipping_line_id = fields.Many2one('line.cost',related="sale_inquiry_id.shipping_line_id")
    shipping_line_ids = fields.Many2many('line.cost', related="sale_inquiry_id.shipping_line_ids")
    partner_shipping_line_id = fields.Many2one('res.partner', related="sale_inquiry_id.partner_shipping_line_id")
    
    free_days = fields.Integer()
    vessel_id = fields.Many2one('vessel',related="sale_inquiry_id.vessel_id")
    voyage_id = fields.Many2one('voyages.detail',related="sale_inquiry_id.voyage_id")
    etd_date = fields.Date('ETD Date', related="sale_inquiry_id.voyage_id.etd_date", readonly=True)
    eta_date = fields.Date('ETA Date', related="sale_inquiry_id.voyage_id.eta_date", readonly=True)
    
    c_month = fields.Char('Month', default=datetime.date.today().month, readonly=True)
    c_year = fields.Char('Year', default=datetime.date.today().year, readonly=True)
    condition_ids = fields.One2many('sale.inquiry.condition', inverse_name='job_id', 
                                    related='sale_inquiry_id.condition_ids',string='Conditions')
    condition_one_ids = fields.One2many('sale.inquiry.condition', inverse_name='job_one_id', 
                                    string='Conditions Table')
    container_size_ids = fields.One2many('sale.inquiry.container', inverse_name='job_id',
                                         string= 'Container Price',related='sale_inquiry_id.container_size_ids')
    container_ids = fields.Many2many('container.size', related="sale_inquiry_id.container_ids")
    
    
    admin_sale_state = fields.Selection([('progress', 'In Progress'), 
                                         ('confirmed', 'Confirmed'), 
                                         ('not_confirmed', 'Not Confirmed')], 
                                         related='sale_inquiry_id.state')
    sea_rate = fields.Float(related='sale_inquiry_id.sea_rate',string='Sea Rate #######')
    insurance_cost_id = fields.Many2one('insurance.cost', string='Insurance Cost',
                                        related="sale_inquiry_id.insurance_cost_id")
    insurance_cost_ids = fields.Many2many('insurance.cost', related="sale_inquiry_id.insurance_cost_ids")
    insurance_rate = fields.Monetary(related="sale_inquiry_id.insurance_rate")
    transport_rate = fields.Float(related="sale_inquiry_id.transport_rate")
    clearance_id = fields.Many2one('clearance.cost',string='Clearance',
                                   related="sale_inquiry_id.clearance_id")
    clearance_cost_ids = fields.One2many('sale.clearance.cost.line', 
                                         inverse_name='job_id', string='Clearance Cost'
                                         ,related='sale_inquiry_id.clearance_cost_ids')
    
    additional_cost_ids = fields.One2many('inquiry.additional.cost', 
                                          inverse_name='job_id',
                                          related='sale_inquiry_id.additional_cost_ids', 
                                          string='Additional Cost')

#   Transport details  
    transporter_cost_id = fields.Many2one('transport.cost', string='Transport',
                                          related="sale_inquiry_id.transporter_cost_id")
    transporter_free_days = fields.Integer(related='sale_inquiry_id.transporter_free_days', string='Transport Free Days')
#     transporter_name = fields.Char(related='transporter_cost_id.partner_id', string='Transporter name')
    transporter_total = fields.Monetary(related='sale_inquiry_id.transporter_total', string='Transport Total')
    currency_id = fields.Many2one('res.currency',related='sale_inquiry_id.currency_id', string="Currency")
#   Commodity key
    commodity_ids = fields.Many2many('commodity', related='sale_inquiry_id.commodity_ids')  

#   JOB FIELDS 
    booking_no = fields.Char(string='Booking No')
    booking_date = fields.Date(string='Booking Date')
    booking_confirmation = fields.Date(string='Book Confirm Date')
    contract_no = fields.Char(string='Contract No')
    price_owner = fields.Many2one('res.partner', string='Price Owner', default=1)
    empt_container_depot = fields.Many2one('res.partner', string='Empty Container Depot')
    analytic_account = fields.Many2one('account.analytic.account', string='Analytical Account')
    Bill_Lading_No = fields.Char (string='Bill Of Lading No.') 
    issue_bill_lading_to = fields.Many2one ('res.partner', related='sale_inquiry_id.issue_bill_lading_to', string='Issue Bill of lading To')
#   Tracking fields 
    act = fields.Char('ACT')
    container_loaded_truck = fields.Char('Container Loaded on Truck') 

#   Driver Details      
    driver_ids = fields.One2many('driver.info', 
                                          inverse_name='job_driver_id', 
                                          string='Driver')
#   route ID
    route_ids = fields.One2many('route', 
                                          inverse_name='job_route_id', 
                                          string='Route')  

    added_con = fields.Boolean()
    added_route = fields.Boolean()
    added_doc = fields.Boolean()
    added_ana_acct = fields.Boolean()
    added_po = fields.Boolean()
    added_po_ins = fields.Boolean()
    
    commodity_line_ids = fields.One2many('job.commodity.line','job_id')
    commodity_line_one_ids = fields.One2many('job.commodity.line','job_one_id')
    
    @api.multi
    def add_analytic_acct(self):
        for rec in self:
            if not rec.analytic_account:
                rec.ensure_one()
                rec.analytic_account.create({'name':rec.name,
                                             'code':rec.name})
                ana_acct_obj = rec.env['account.analytic.account'].search([('name','=',rec.name)])
                rec.write({'analytic_account':ana_acct_obj.id,
                           'added_ana_acct':True})
                rec.message_post(body="Analytic account has been added")
            else:
                raise UserError("This 'Job' is already assigned to an 'Analytic account'.")
    
    @api.multi
    def add_po(self):
        for rec in self:
            if not rec.analytic_account:
                raise UserError("Please add 'Analytic Account' first.")
            else:
                if rec.analytic_account and rec.customs_dec_id and rec.clearance_id:
                    product_job_obj=rec.env['product.product'].search([('name','=','Clearance Services')])
                    if not product_job_obj:
                        rec.ensure_one()
                        product_obj=rec.env['product.product']
                        product_cat_obj=rec.env['product.category'].search([('name','=','All')])
                        product_obj.create({'name':'Clearance Services',
                                            'sale_ok':True,
                                            'purchase_ok':True,
                                            'type':'service',
                                            'categ_id':product_cat_obj.id})
                        product_job_obj=rec.env['product.product'].search([('name','=','Clearance Services')])
                        product_unit_mesure_obj=rec.env['uom.uom'].search([('name','=','Unit(s)')])
                        po_obj=rec.env['purchase.order']
                        po_obj.create({'partner_id':rec.clearance_id.partner_id.id,
                                       'partner_ref':rec.clearance_id.qut_number,
                                       'currency_id':rec.clearance_id.currency_id.id,
                                       'payment_term_id':rec.clearance_id.payment_term_id.id,
                                       'order_line':[(0,0, {'product_id':product_job_obj.id,
                                                            'name':product_job_obj.name,
                                                            'sale_ok':True,
                                                            'purchase_ok':True,
                                                            'type':'service',
                                                            'product_qty':1,
                                                            'product_uom':product_unit_mesure_obj.id,
                                                            'date_planned': rec.create_date,
                                                            'account_analytic_id':rec.analytic_account.id,
                                                            'price_unit':sum(rec.clearance_cost_ids.mapped('cost')+[0])})]
                                                            })
                        rec.write({'added_po':True})
                        rec.message_post(body="Clearance Purchase order has been added")
                    else:
                        product_job_obj=rec.env['product.product'].search([('name','=','Clearance Services')])
                        if product_job_obj:
                            product_job_obj=rec.env['product.product'].search([('name','=','Clearance Services')])
                            product_unit_mesure_obj=rec.env['uom.uom'].search([('name','=','Unit(s)')])
                            po_obj=rec.env['purchase.order']
                            po_obj.create({'partner_id':rec.clearance_id.partner_id.id,
                                           'partner_ref':rec.clearance_id.qut_number,
                                           'currency_id':rec.clearance_id.currency_id.id,
                                           'payment_term_id':rec.clearance_id.payment_term_id.id,
                                           'order_line':[(0,0, {'product_id':product_job_obj.id,
                                                                'name':product_job_obj.name,
                                                                'sale_ok':True,
                                                                'purchase_ok':True,
                                                                'type':'service',
                                                                'product_qty':1,
                                                                'product_uom':product_unit_mesure_obj.id,
                                                                'date_planned': rec.create_date,
                                                                'account_analytic_id':rec.analytic_account.id,
                                                                'price_unit':sum(rec.clearance_cost_ids.mapped('cost')+[0])})]
                                                                })
                            rec.write({'added_po':True})
                            rec.message_post(body="Clearance Purchase order has been added")
    
    @api.multi
    def add_po_insurance(self):
        for rec in self:
            if not rec.analytic_account:
                raise UserError("Please add 'Analytic Account' first.")
            else:
                if rec.analytic_account and rec.insurance_cost_id and rec.insurance_rate:
                    product_job_obj=rec.env['product.product'].search([('name','=','Insurance Policy Fees')])
                    if not product_job_obj:
                        rec.ensure_one()
                        product_obj=rec.env['product.product']
                        product_cat_obj=rec.env['product.category'].search([('name','=','All')])
                        product_obj.create({'name':'Insurance Policy Fees',
                                            'sale_ok':True,
                                            'purchase_ok':True,
                                            'type':'service',
                                            'categ_id':product_cat_obj.id})
                        product_job_obj=rec.env['product.product'].search([('name','=','Insurance Policy Fees')])
                        product_unit_mesure_obj=rec.env['uom.uom'].search([('name','=','Unit(s)')])
                        po_obj=rec.env['purchase.order']
                        po_obj.create({'partner_id':rec.insurance_cost_id.partner_id.id,
                                       'partner_ref':rec.insurance_cost_id.qut_number,
                                       'currency_id':rec.insurance_cost_id.currency_id.id,
                                       'payment_term_id':rec.insurance_cost_id.payment_term_id.id,
                                       'order_line':[(0,0, {'product_id':product_job_obj.id,
                                                            'name':product_job_obj.name,
                                                            'sale_ok':True,
                                                            'purchase_ok':True,
                                                            'type':'service',
                                                            'product_qty':1,
                                                            'product_uom':product_unit_mesure_obj.id,
                                                            'date_planned': rec.create_date,
                                                            'account_analytic_id':rec.analytic_account.id,
                                                            'price_unit':rec.insurance_rate})]
                                                            })
                        rec.write({'added_po_ins':True})
                        rec.message_post(body="Insurance Policy Purchase order has been added")
                    else:
                        product_job_obj=rec.env['product.product'].search([('name','=','Insurance Policy Fees')])
                        if product_job_obj:
                           product_job_obj=rec.env['product.product'].search([('name','=','Insurance Policy Fees')])
                           product_unit_mesure_obj=rec.env['uom.uom'].search([('name','=','Unit(s)')])
                           po_obj=rec.env['purchase.order']
                           po_obj.create({'partner_id':rec.insurance_cost_id.partner_id.id,
                                           'partner_ref':rec.insurance_cost_id.qut_number,
                                           'currency_id':rec.insurance_cost_id.currency_id.id,
                                           'payment_term_id':rec.insurance_cost_id.payment_term_id.id,
                                           'order_line':[(0,0, {'product_id':product_job_obj.id,
                                                                'name':product_job_obj.name,
                                                                'sale_ok':True,
                                                                'purchase_ok':True,
                                                                'type':'service',
                                                                'product_qty':1,
                                                                'product_uom':product_unit_mesure_obj.id,
                                                                'date_planned': rec.create_date,
                                                                'account_analytic_id':rec.analytic_account.id,
                                                                'price_unit':rec.insurance_rate})]
                                                                })
                           rec.write({'added_po_ins':True})
                           rec.message_post(body="Insurance Policy Purchase order has been added")
                    
            
                     

    @api.multi  
    def call_purchase(self):  
        mod_obj = self.env['ir.model.data']
        try:
            kanban_res = mod_obj.get_object_reference('purchase_order', 'view_purchase_order_kanban')[1]
            tree_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
            form_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = kanban_res= False
        return {  
            'name': ('purchase.order.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[kanban,tree,form]",  
            'res_model': 'purchase.order',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form'), (kanban_res, 'kanban')], 
            'domain': [('order_line.account_analytic_id.id','=',self.analytic_account.id)], 
            'target': 'current',  
               }
    
    @api.multi  
    def call_insurance_smart(self):  
        mod_obj = self.env['ir.model.data']
        try:
            kanban_res = mod_obj.get_object_reference('purchase_order', 'view_purchase_order_kanban')[1]
            tree_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
            form_res = mod_obj.get_object_reference('purchase_order', 'purchase_order_tree')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = kanban_res= False
        return {  
            'name': ('purchase.order.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[kanban,tree,form]",  
            'res_model': 'purchase.order',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form'), (kanban_res, 'kanban')], 
            'domain': [('order_line.account_analytic_id.id','=',self.analytic_account.id)], 
            'target': 'current',  
               }
    
    @api.multi  
    def call_doc(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('documents', 'documents_view_list')[1]
            form_res = mod_obj.get_object_reference('documents', 'documents_view_form')[1]
            search_res = mod_obj.get_object_reference('base', 'view_attachment_search')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('attachments form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[tree,form,search]",  
            'res_model': 'ir.attachment',  
            'view_id': False,  
            'views': [(tree_res, 'tree'),(form_res, 'form'),(search_res, 'search')], 
            'domain': [('folder_id.name','=',self.name)], 
            'target': 'current',  
               } 
    
    @api.multi  
    def call_tickets(self):  
        mod_obj = self.env['ir.model.data']
        try:
            kanban_res = mod_obj.get_object_reference('helpdesk', 'helpdesk_ticket_view_kanban')[1]
            tree_res = mod_obj.get_object_reference('helpdesk', 'helpdesk_tickets_view_tree')[1]
            form_res = mod_obj.get_object_reference('helpdesk', 'helpdesk_ticket_view_form')[1]
            search_res = mod_obj.get_object_reference('helpdesk', 'helpdesk_tickets_view_search')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('helpdesk.ticket.form'),  
            'type': 'ir.actions.act_window',  
            'view_type': 'form',  
            'view_mode': "[kanban,tree,form,search]",  
            'res_model': 'helpdesk.ticket',  
            'view_id': False,  
            'views': [(kanban_res, 'kanban'),(tree_res, 'tree'),(form_res, 'form'),(search_res, 'search')], 
            'domain': [('job_id','=',self.id)], 
            'target': 'current',  
               } 
        
    @api.multi
    def add_job_folder(self):
        """
        Check if there is Jobs dir at document.
        Create subfolder inside the Jobs folder.
        """
        for rec in self:
            doc_obj = self.env['documents.folder']
            l=doc_obj.search([('name','=','Jobs')])
            if not l:
                raise UserError('Please add Jobs directory at document first.')
            else:
                rec.ensure_one()
                doc_obj.create({'name':rec.name,
                                'parent_folder_id':l.id})
                rec.write({'added_doc':True})

    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        d_id = super(Job, self).create(vals_list)
        for val in d_id:
            val['name'] = self.env['ir.sequence'].next_by_code('job.seq')
        for val in d_id:
            if val.driver_ids:
                for i in range(4):
                    val.write({'driver_ids':[(0,0, {'container_no':0})]}) 
        return d_id 
    
    @api.multi
    def add_con_lines(self):
        for rec in self:
            if rec.container_size_ids.container_qty > 0:
                con_no_count = rec.container_size_ids.container_qty
                i = 0
                for i in range(int(con_no_count)):
                    rec.write({'driver_ids':[(0,0, {'container_no':0})],'added_con':True})
                    i = i + 1
            else:
                raise UserError("Container QTY should be more than 0")   
            
    @api.multi
    def add_route(self):
        """add start and end point of the Freight""" 
        for rec in self:
            if rec.place_loading_id:
                rec.write({'route_ids':[(0,0, {'shipment_method':'land_freight',
                                               'country_id':rec.country_loading_id.id,
                                               'state_id':rec.state_loading_id.id,
                                               'city_id':rec.city_loading_id.id})],'added_route':True})
            elif rec.empt_container_depot:
                rec.write({'route_ids':[(0,0, {'shipment_method':'land_freight',
                                               'country_id':rec.empt_container_depot.country_id.id,
                                               'state_id':rec.empt_container_depot.state_id.id,
                                               'city_id':rec.empt_container_depot.city_id.id})],'added_route':True})
            
        
        
        
        
        
        
         
   
    
  
        
