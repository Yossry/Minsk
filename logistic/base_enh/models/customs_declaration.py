# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomsDeclaration(models.Model):
    _name = 'customs.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "CustomsDeclaration"
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s | %s'%(record.name,record.code)))

        return result
    
