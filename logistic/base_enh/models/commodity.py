# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Commodity(models.Model):
    _name = 'commodity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Commodity"
    
    name = fields.Char ('Name')
    temperature = fields.Float('Temperature')
    warehouse_condition = fields.Char('Warehouse condition')
    warehouse_condition_att = fields.Binary(attachment=True,string="Attachment Ware")
    transport_condition = fields.Char('Transport condition')
    transport_condition_att = fields.Binary(attachment=True,string="Attachment Trans")
    port_condition = fields.Char('Port condition')
    port_condition_att = fields.Binary(attachment=True,string="Attachment Port")
    other_condition = fields.Char('Other condition')
    other_condition_att = fields.Binary(attachment=True,string="Attachment Other")
    commodity_category = fields.Many2one('commodity', string='Commodity Category', domain=[('is_category','=',True)])
    UN_No = fields.Char("UN No")
    IMCO_Class = fields.Char("IMCO Class")
    HS_Code = fields.Char("HS Code")
    is_document = fields.Boolean("Is Document")
    active=fields.Boolean(default=True)
    note = fields.Text('Note')
    is_category = fields.Boolean("Is Category")
    package_ids=fields.Many2many('packaging',string='Package')

    @api.onchange('is_category')
    def erase_commodity_category(self):
        for rec in self:
            rec.commodity_category=u''
            rec.package_ids=u''