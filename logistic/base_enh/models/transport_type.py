# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TransportType(models.Model):
    _name = 'transport.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "TransportType"
    
    name = fields.Char('Name',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
    
