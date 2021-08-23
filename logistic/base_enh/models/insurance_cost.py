# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class InsuranceCondition(models.Model):
    _name = 'insurance.condition'
    _description = "InsuranceCondition"
    
    name = fields.Char(required=True)
    type = fields.Many2one('insurance.items',required=True)
    cost_id = fields.Many2one('insurance.cost',ondelete='cascade')
    
    
class AdditionalInsuCost(models.Model):
    _name = 'insurance.cost.line'
    _description = "AdditionalInsuCost"
    
    product_id = fields.Many2one('product.product', string='Additional Name', required=True,
                                 domain=[('is_add_cost', '=', True)] )
    cost = fields.Monetary(string="Cost")
    cost_id = fields.Many2one('insurance.cost', string="Line Cost")
    currency_id = fields.Many2one('res.currency', string="Currency")

class InsuranceCostNote(models.Model):
    _name='insurance.cost.note'
    _description='insurance.cost.note'
    
    note=fields.Text()
    insurance_id=fields.Many2one('insurance.cost')
    
class InsuranceItems(models.Model):
    _name = 'insurance.items'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "InsuranceItems"
    
    name=fields.Char('Name')
    note=fields.Text('Note')
    active=fields.Boolean(default=True)
    
class InsuranceCost(models.Model):
    _name = 'insurance.cost'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'qut_number'
    _description = "InsuranceCost"
    
    partner_id = fields.Many2one('res.partner',string="Insurance Company",domain=[('is_insurance_company', '=', True)])
    qut_number =fields.Char('Quotation Number')
    date = fields.Date('Date')
    country_loading_id = fields.Many2one('res.country',string="Country Of Loading")
    state_loading_id = fields.Many2one('res.country.state', string="State Of Loading")
    city_loading_id= fields.Many2one('res.city',string='City Of Loading')
    country_dest_id = fields.Many2one('res.country',string="Country Of Destination")
    state_dest_id = fields.Many2one('res.country.state', string="State Of Destination")
    city_dest_id = fields.Many2one('res.city',string='City Of  Destination')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    insurance_type_id = fields.Many2one('insurance.type',string="Insurance Type")
    rate = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string="Currency")
    note = fields.Text()
    total = fields.Monetary(compute="_compute_total")
    cost_line_ids = fields.One2many('insurance.cost.line','cost_id',string="Additional Cost")
    condition_ids = fields.One2many('insurance.condition','cost_id',string="Condition")
    
    
    is_expired = fields.Boolean('Is Expired Price',compute='_compute_is_expired',search="_search_is_expired")
    is_next = fields.Boolean(compute='_compute_is_expired',search="_search_is_next")
    active=fields.Boolean(default=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms", 
                                      related='partner_id.property_supplier_payment_term_id')
    insur_cost_note_ids=fields.One2many('insurance.cost.note', 'insurance_id')
    transport_type=fields.Many2many('transport.type', string='Transport Type')
    cif_type=fields.Selection([('percentage','Percentage'),('amount','Amount')],string='CIF Type')
    cif_perc=fields.Float('CIF')
    cif_amount=fields.Monetary('CIF')
    voyage_from=fields.Many2one('port',string='Voyage From')
    voyage_to=fields.Many2one('port',string='Voyage To')
    beneficiary=fields.Selection([('royal_line','Royal line'),('partner','Partner')
                                  ,('bank','Bank'),('others','Others')], string='Beneficiary')
    @api.constrains('rate')
    def rate_value(self):
        """
        Rate must be more than 0
        """
        for rec in self:
            if rec.rate <= 0:
                raise UserError("'Rate' value should be more than 0.")
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
            'domain': [('insurance_cost_id.id', '=', self.id)], 
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
            'domain': [('insurance_cost_id.id', '=', self.id)], 
            'target': 'current',  
               }
    
    @api.onchange('partner_id')
    def clear_insurance_company_related(self):
        """
        Clear qut_number,country_loading_id,rate,currency_id
        country_dest_id,from_date,to_date,insurance_type_id
        cost_line_ids,condition_ids
        """
        for rec in self:
            rec.qut_number=u''
            rec.country_loading_id=u''
            rec.rate=u''
            rec.currency_id=u''
            rec.country_dest_id=u''
            rec.from_date=u''
            rec.to_date=u''
            rec.insurance_type_id=u''
        for l in self.cost_line_ids:
            l.unlink()
        for n in self.condition_ids:
            n.unlink()
    
    @api.onchange('country_loading_id')
    def clear_country_loading_related(self):
        """
        Clear state_loading_id, ciity_loading_id once 
        country_loading_id changed or cleared.
        """
        for rec in self:
            rec.state_loading_id=u''
            rec.city_loading_id=u''
    
    @api.onchange('country_dest_id')
    def clear_country_destination_related(self):
        """
        Clear state_dest_id, ciity_dest_id once 
        country_dest_id changed or cleared.
        """
        for rec in self:
            rec.state_dest_id=u''
            rec.city_dest_id=u''
            
    @api.constrains('to_date','from_date')
    def check_date(self):
        """From date should be <= to date"""
        for rec in self:
            if rec.from_date > rec.to_date:
                raise UserError("'From date' should be less than or equal 'To date'")
            
    def _search_is_expired(self,op,val):
        sql = """
select id from insurance_cost where to_date <= '%s'
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
select id from insurance_cost where from_date > '%s'
"""%fields.Date.today()
        self._cr.execute(sql)
        ids = self._cr.fetchall()
        ids = [id[0] for id in ids]
        if val and op == '=' or not val and op == '!=':
            domain = [('id','in', ids)]
        else :
            domain = [('id','not in', ids)]
        return domain
    
    
    
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
    
    @api.depends('rate','cost_line_ids','cost_line_ids.cost')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.rate + sum(rec.mapped('cost_line_ids.cost')+[0])
        
        
        
        
    