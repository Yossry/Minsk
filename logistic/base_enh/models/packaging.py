# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Packaging(models.Model):
    _name = 'packaging'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Packaging"
    
    name = fields.Char('Name',required=True)
    CBM = fields.Integer('CBM')
    note = fields.Text('Note')
    active = fields.Boolean('Active', default=True)