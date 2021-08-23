# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerClass(models.Model):
    _name = 'customer.class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "CustomerClass"
    
    name = fields.Char('Name',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
    
