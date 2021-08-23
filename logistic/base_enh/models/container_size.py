# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class ContainerSize(models.Model):
    _name = 'container.size'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "size"
    _description = "ContainerSize"
    
    size = fields.Char('Size',required=True)
    type = fields.Selection([ 
                             ('dry', 'Dry'), 
                             ('refrigerant', 'Refrigerant'),
                             ('special_equipment', 'Special Equipment')], 
                             string="Type")
    note = fields.Char('Note')
    TEU = fields.Char('TEU')
    image = fields.Binary(attachment=True)
    active=fields.Boolean(default=True)
