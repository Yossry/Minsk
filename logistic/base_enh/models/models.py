# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import UserError
from os import linesep

class SalePerson(models.Model):
    _name = "sale.person"
    _description = "SalePerson"
    
    user_id = fields.Many2one('res.users',required=True,inverse="_inverse_sale_id")
    type = fields.Selection([('sale','Sales'),
                             ('operation','Operation'),
                             ('follow','Follow')],required=True,inverse="_inverse_sale_id")
    from_date = fields.Date('From Date',required=True, default='2018-12-01')
    to_date = fields.Date('To Date',required=True, default='2020-12-31')
    is_active = fields.Boolean('Active',inverse="_inverse_sale_id", default=True)
    partner_id = fields.Many2one('res.partner')
    
    
    @api.multi
    def _inverse_sale_id(self):
        for rec in self:
            if len(rec.partner_id.sale_person_ids.filtered(lambda x:x.is_active and x.type =='sale'))>1:
                raise UserError("You Cannot has more than active sales person")
            if rec.type == 'sale' and rec.is_active:
                rec.partner_id.user_id = rec.user_id.id
            elif rec.type == 'sale' and not  rec.is_active and rec.user_id.id == rec.partner_id.user_id.id:
                rec.partner_id.user_id = False
                
                
                
                
                
    
    
                
        
    

class ResPlace(models.Model):
    _name = 'res.place'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'address'
    _description = "ResPlace"
    
    country_id = fields.Many2one('res.country',required=True)
    city_id = fields.Many2one('res.city',required=True)
    state_id = fields.Many2one('res.country.state')
    is_port = fields.Boolean('Is Terminal')
    port_id = fields.Many2one('port')
    address = fields.Text('Address',required=True)
    is_delivery_place = fields.Boolean('Is Delivery Place') 
    zip_code = fields.Integer('ZIP Code')
    active=fields.Boolean(default=True)
    
    @api.onchange('country_id')
    def place_erase(self):
        """Erase data from City, state, address, zipcode and Port"""
        self.city_id=u''
        self.state_id=u''
        self.address=u''
        self.zip_code=u''
        self.port_id=u''
    
    @api.onchange('is_port')
    def port_erase(self):
        for rec in self:
            self.port_id=u''
        
    @api.onchange('state_id')
    def erase_state_related(self):
        for rec in self:
            rec.city_id = u''
            rec.port_id = u''
            rec.address = u''
        
class Port(models.Model):
    _name = 'port'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Port"

    name = fields.Char(string='Name',required=True)
    code = fields.Char(string='Code')
    type = fields.Selection([('air',"Air"),('sea',"Sea"),('dry',"Dry")],required=True,default='air')
    country_id = fields.Many2one('res.country',stirng="Country",required=True)
    state_id = fields.Many2one('res.country.state','State')
    port_type = fields.Many2many('port.type', string='Port Type',required=True)
    city_id = fields.Many2one('res.city',required=True)
    active=fields.Boolean(default=True)
    @api.onchange('country_id')
    def erase_country_related(self):
        """Erase related fields to 'Country' once empty or changed"""
        for rec in self:
            rec.state_id=u''
            rec.city_id=u''
    
    @api.onchange('state_id')
    def erase_state_related(self):
        """erase related fields to state once empty or changed"""
        for rec in self:
            rec.city_id=u''

class HelpdeskTicket(models.Model):
    _inherit="helpdesk.ticket"
    _description="helpdesk.ticket"
     
    job_id=fields.Many2one('job')  
    partner_id=fields.Many2one('res.partner', related='job_id.partner_id', store=True)     
    
class PortType(models.Model):
    _name = 'port.type'
    _description = "PortType"
     
    name = fields.Char('Name')
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = "HrEmployee"
    
    local_name = fields.Char("Local Name")

class ResCity(models.Model):
    _inherit="res.city"
    _description = "ResCity"
    
    code = fields.Char("Code")
    local_name = fields.Char("Local Name")
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = "ResPartner"

    is_courier = fields.Boolean('Is Courier')
    is_shipper = fields.Boolean('Is Shipper')
    is_consignee = fields.Boolean('Is Consignee')
    is_notify = fields.Boolean('Is notify Party')
    is_agent = fields.Boolean('Is Agent')
    is_diver = fields.Boolean('Is Driver')
    is_customs_point = fields.Boolean('Is Customs point')
    is_competitor = fields.Boolean('Is Competitor')
    is_sea_line = fields.Boolean('Is Sea Line')
#   airline details  
    is_air_line = fields.Boolean('Is Air Line')
    iata_code=fields.Char('IATA Code')
    cass_code=fields.Char('CASS Code')
    icao_code=fields.Char('ICAO Code')
#   airline details end here
  
    is_clearance_company= fields.Boolean('Is Clearance Company')
    is_transporter_company= fields.Boolean('Is Transporter Company')
    is_insurance_company= fields.Boolean('Is Insurance Company')
    is_depot = fields.Boolean('Is Depot')

    phone_ids = fields.One2many('res.phone','partner_id', string='Phones Number')
    
    sea_ids = fields.One2many('sea.lines','partner_id')
    bill_fees = fields.Monetary('Bill Fees')
    release_to_bill = fields.Monetary('Bill of Lading To Release')
    amendment_fees = fields.Monetary('Amendment Fees')
    late_payment = fields.Monetary('Late Payment')
    
    customs_id = fields.Many2one('res.partner',string="Customs point",domain=[('is_customs_point','=',True)])
    customer_class_id = fields.Many2one('customer.class')

    plate_code = fields.Char('Plate Code')
    plate_number = fields.Char('Plate Number')
    country_nati_id = fields.Many2one(
        'res.country', 'Nationality (Country)')
    country_truck_id = fields.Many2one(
        'res.country', 'Truck Nationality')
    truck_type_id = fields.Many2one('truck.type')
    
    cheek_name = fields.Char('Cheek Name')
    
    product_ids = fields.Many2many('product.product')
    
    sale_person_ids= fields.One2many('sale.person','partner_id')
    

#   City local name   
    local_name = fields.Char("Local Name")
    
#   gogle map field display at contact form.   
    google_map_partner = fields.Char(string="Map")

#   commodity ids
    commodity_ids = fields.Many2many('commodity')  
    job_id = fields.Many2one ('job')
    job_position_id = fields.Many2one('job.position', string="Staff Job Position")
    customer = fields.Boolean(string='Is a Customer', default=False,
                               help="Check this box if this contact is a customer. It can be selected in sales orders.")
    street_number2 = fields.Char('P.O. Box', compute='_split_street', help="Door Number",
                                 inverse='_set_street', store=True)
    street_number = fields.Char(string='Building No.')
    street_name = fields.Char()
    street2 = fields.Char(required=True)
#   DHL Logistic id  
    dhl_log_id = fields.Many2one('dhl.logistic')
    dhl_log_to_id = fields.Many2one('dhl.logistic')
    
    @api.multi
    def name_get(self):
        if 'custom_point' in self._context:
            lines = []
            for record in self:
                name = (record.name + ' | ' + record.parent_id.name) if record.parent_id else record.name
                lines.append((record.id,name))
            return linese
        lines = []
        for record in self:
            name = record.name + ' | ' + str(record.plate_code) + ' | '+ str(record.plate_number) if record.is_diver else record.name
            lines.append((record.id,str(name)))
        return lines
        return super(ResPartner, self).name_get()
#     @api.multi
#     def name_get(self):
#         lines = []
#         for rec in self:
#             name = (rec.name + ' | ' + str(rec.) + ' | ' + str(rec.))
#             lines.append(rec.id,name)
#         return lines
#     @api.multi
#     def name_get(self):
#         lines = []
#         for record in self:
#             name = record.name + ' | ' + str(record.plate_code) + ' | '+ str(record.plate_number) 
#             lines.append((record.id,str(name)))
#         return lines
        
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if 'customs_filter' in self._context and self._context.get('from_customs_filter',True):
            if not self._context.get('customs_filter'):
                args = expression.AND([args] + [[('id','in',[])]])
            else:
                partner_id = self.env['res.partner'].browse(self._context.get('customs_filter' ))
                args = expression.AND([args] + [[('id','in',partner_id.with_context(from_customs_filter=False).child_ids.mapped('customs_id').ids)]])
        res =  super(ResPartner, self)._search( args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        if self.env.user.has_group('base_enh.res_partner_limit_access_group'):
            res  = list(set(res) & set(self.env['sale.person'].search([('user_id', '=', self.env.user.id),('is_active', '=', True)]).mapped('partner_id.id')))
        return res
    
#     @api.multi
#     def read(self, fields=None, load='_classic_read'):
#         if self.env.user.has_group('base_enh.res_partner_limit_access_group'):
#             self  = self & self.env['sale.person'].search([('user_id', '=', self.env.user.id),('is_active', '=', True)]).mapped('partner_id')
#         return super(ResPartner, self).read(fields,load)
        
    @api.onchange('city_id')
    def _onchange_city_id(self):
        pass
    def open_vessels(self):
        action = self.env.ref('base_enh.vessel_action').read()[0]
        action['domain'] = [('sea_line_id','=',self.id)]
        action['context'] = {'default_sea_line_id':self.id}
        return action
    
    
class ResPhone(models.Model):
    _name = 'res.phone'
    _description = "ResPhone"
    
    name = fields.Char('Number',required=True)
    note = fields.Char('Note')  
    partner_id = fields.Many2one('res.partner')
    
    
class SeaLines(models.Model):
    _name="sea.lines"
    _description = "SeaLines"
    
    container_size_id = fields.Many2one('container.size',string="Container Size")
    name = fields.Char(related="container_size_id.size")
   
    type = fields.Selection([('import','Import'),('export','Export'),('cross','Cross')])
    free_days = fields.Integer('Free Days')
    first_demurrage_from = fields.Integer('First Way Demurrage From', default='1', readonly=True)
    first_demurrage_to = fields.Integer('First Way Demurrage To', default='2')
    first_rate =  fields.Monetary('First Way Demurrage Rate') 
    second_demurrage_from = fields.Integer('Second Way Demurrage From', 
                                           readonly=True, 
                                           compute='_value_second_way')
    second_demurrage_to = fields.Integer('Second Way Demurrage To')
    second_rate =  fields.Monetary('Second Way Demurrage Rate')
    third_demurrage_from = fields.Integer('Third Way Demurrage From',
                                           readonly=True, 
                                           compute='_value_second_way')
    third_demurrage_to = fields.Integer('Third Way Demurrage To',
                                         default='1095')
    third_rate =  fields.Monetary('Third Way Demurrage Rate')
    delivery_order = fields.Monetary('Delivery Order')
    agency = fields.Monetary('Agency')
    partner_id = fields.Many2one('res.partner')
    currency_id = fields.Many2one('res.currency', string="Currency", related='partner_id.currency_id', readonly=True)
    
    @api.constrains('first_demurrage_from','first_rate',
                    'second_demurrage_from','second_rate')
    def check_first_dem_from(self):
        for rec in self:
            if rec.first_demurrage_to <= rec.first_demurrage_from:
                raise UserError("'First Way Demurrage To' should be greater than 'First Way Demurrage From'!")
            if rec.type in ['export', 'import']:
                if rec.first_rate <= 0:
                    raise UserError("'First Way Demurrage Rate' should be not '0'!")
            if rec.second_demurrage_to <= rec.second_demurrage_from:
                raise UserError("'Second Way Demurrage To' should be greater than 'Second Way Demurrage From'!")
            if rec.type in ['export', 'import']:
                if rec.second_demurrage_to <= 0:
                    raise UserError("'Second Way Demurrage To' should be not '0'!")
            if rec.type in ['export', 'import']:
                if rec.second_rate <= 0:
                    raise UserError("'Second Way Demurrage Rate' should be not '0'!")
            if rec.third_demurrage_to <= rec.third_demurrage_from:
                raise UserError("'Third Way Demurrage To' should be greater than 'Third Way Demurrage From'!")
            if rec.type in ['export', 'import']:
                if rec.third_rate <=0:
                    raise UserError("'Third Way Demurrage Rate' should be greater than '0'")
    
    @api.depends('first_demurrage_to','second_demurrage_to')
    def _value_second_way(self):
        for rec in self:
            rec.second_demurrage_from = rec.first_demurrage_to + 1
        for rec in self:
            rec.third_demurrage_from = rec.second_demurrage_to + 1

    @api.multi
    def name_get(self):
        lines = []
        for record in self:
            name = str(record.name) + ' | ' + str(record.type)
            lines.append((record.id,str(name)))
        return lines
    
    
    
     
    

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = "ResUsers"
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        operation_filter = self._context.get('operation_filter',0)
        if operation_filter is False:
            raise UserError('Must select a customer first')
        elif operation_filter:
            ids =  self.env['sale.person'].search([('type','=','operation'),('partner_id','=',operation_filter)]).mapped('user_id').ids
            args = expression.AND([args] + [[('id','in',ids)]])
        return super(ResUsers, self)._search(args, offset, limit, order, count, access_rights_uid)
    
class ExtraServices(models.Model):
    _name = 'extra.services'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "ExtraServices"
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    note = fields.Text('Note')
    active = fields.Boolean('Active',default=True)

class WareHouse (models.Model):
    _name = 'ware.house'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "WareHouse"
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    note = fields.Text('Note')
    type = fields.Selection([('terminal','Terminal'),('bonded','Bonded'),('others','Others')],  default='terminal', string='Type')
    terminal_code = fields.Char('Terminal Code')
    address = fields.Text('Address')
    image = fields.Binary(attachment=True)
    active = fields.Boolean('Active',default=True)
    image_attachment = fields.Binary(attachment=True,string="Image Attachment")
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one('res.country.state', string="State")
    city_id = fields.Many2one('res.city', 'City')
    place_id = fields.Many2one('res.place','Place')
    port_id = fields.Many2one('port', 'Port')
    terminal_id = fields.Many2one('res.place', 'Terminal', domain=[('is_port','=',True)])
    
    @api.onchange('country_id')
    def erase_country_re(self):
        for rec in self:
            rec.state_id=u''
            rec.city_id=u''
            rec.place_id=u''
            rec.port_id=u''
            rec.terminal_id=u''
    
    @api.onchange('state_id')
    def erase_state_re(self):
        for rec in self:
            rec.city_id=u''
    
    @api.onchange('city_id')
    def erase_city_re(self):
        for rec in self:
            rec.place_id=u''
            rec.terminal_id=u''
            rec.port_id=u''
    
    @api.onchange('port_id')
    def erase_port_re(self):
        for rec in self:
            rec.terminal_id=u''
    
class MITCompanies (models.Model):
    _name = 'mit.companies'
    _description = "MITCompanies"
    
    company_No = fields.Char ('Company No.')
    name = fields.Char ('name')
    type = fields.Selection([('1','ذات مسؤولية محدودة'),
                             ('2','أجنبية - فرع عامل'),
                             ('3','أجنبية-فرع غير عامل'),
                             ('4','معفاه'),
                             ('5','مساهمة خاصة محدودة'),
                             ('6','تضامن'),
                             ('7','توصية بسيطة'),
                             ('8','عربية مشتركة'),
                             ('9','لا تهدف إلى ربح'),
                             ('10','مدنيه'),
                             ('11','مساهمة عامة محدودة'),
                             ('12','اخرى'),
                             ('13','مؤسسة فردية'),
                             ('14','مناطق حرة'),
                             ('15','جمعيات'),
                             ('16','0'),
                             ],string='Type',default='1',required=True, store=True)
    capital = fields.Integer('Capital')
    registration_date = fields.Datetime('Registration Date')
    city_id = fields.Many2one('res.city',required=True)
    phone = fields.Char ('Phone No')
    mobile = fields.Char ('Mobile No')
    HQ = fields.Char('Head Quarter')
    po_box = fields.Integer ('P.O. Box')
    postal_code = fields.Integer ('Postal Code')
    Email = fields.Char ('Email')
    org_national_no = fields.Char ('Org National No')
    active = fields.Boolean('Active',default=True)
    
    @api.multi  
    def get_trade_name(self):  
        mod_obj = self.env['ir.model.data']
        try:
            tree_res = mod_obj.get_object_reference('trade_name', 'trade_name_list_view')[1]
            form_res = mod_obj.get_object_reference('trade_name', 'trade_name_form_view')[1]
#             search_res = mod_obj.get_object_reference('trade_name', 'view_trade_tran_search1')[1]
        except ValueError:
            form_res = tree_res = search_res = False
        return {  
            'name': ('Trade Name list'),  
            'type': 'ir.actions.act_window',  
            'domain': [],  
            'view_type': 'form',  
            'view_mode': "[tree,form]",  
            'res_model': 'trade.name',  
            'view_id': False,  
            'views': [(tree_res, 'tree'), (form_res, 'form')], 
            'domain': [('registration_No','=',self.company_No),('type', '=', self.type)], 
            'target': 'current',  
               } 

            
class TradeName (models.Model):
    _name = 'trade.name'
    _description = "TradeName"
    
    
    trade_No = fields.Char ('Trade No.')
    city_id = fields.Many2one('res.city',required=True)
    type = fields.Selection([('1','ذات مسؤولية محدودة'),
                             ('2','أجنبية - فرع عامل'),
                             ('3','أجنبية-فرع غير عامل'),
                             ('4','معفاه'),
                             ('5','مساهمة خاصة محدودة'),
                             ('6','تضامن'),
                             ('7','توصية بسيطة'),
                             ('8','عربية مشتركة'),
                             ('9','لا تهدف إلى ربح'),
                             ('10','مدنيه'),
                             ('11','مساهمة عامة محدودة'),
                             ('12','اخرى'),
                             ('13','مؤسسة فردية'),
                             ('14','مناطق حرة'),
                             ('15','جمعيات'),
                             ('16','0'),
                             ],string='Type',default='1',required=True, store=True)
    registration_No = fields.Char ('Registration No.')
    trade_name = fields.Char ('Trade Name')
    registration_date = fields.Datetime('Registration Date')
    state = fields.Text(string='Status')
    owner = fields.Char('Owner')
    active=fields.Boolean(default=True)

class ImporterCard (models.Model): 
    _name = 'importer.card'
    _description = "ImporterCard"
    
    
    card_No = fields.Char ('Card No.')
    name = fields.Char ('Name')
    issue_date = fields.Datetime ('Date of Issue')
    expiry_date = fields.Datetime ('Expiry Date')
    active = fields.Boolean('Active',default=True)
    
class IndividualEstablishment (models.Model):
    _name = 'individual.establishment'
    _description = "IndividualEstablishment"
    
    
    ind_No = fields.Char ('Indiv Estab No.')
    city_id = fields.Many2one('res.city',required=True)
    registeration_date = fields.Datetime ('Registration Date')
    capital = fields.Integer('Capital')
    owner_nationality = fields.Char ('Owner Nationality')
    state = fields.Char(string='Status')
    status_date = fields.Datetime ('Status Date')
    National_ID = fields.Char ('National ID')
    establishment_name = fields.Char ('Establishment Name')
    trade_name = fields.Char ('Trade Name')
    place_id = fields.Many2one('res.place',required=True)
    street = fields.Char ('Street')
    active=fields.Boolean(default=True)
    
    
    
    
    
    
    
    
    
     