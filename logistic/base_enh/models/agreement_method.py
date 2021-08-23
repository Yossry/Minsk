# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AgreementMethod(models.Model):
    _name = 'agreement.method'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "AgreementMethod"
    
    name = fields.Char('Name',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
    
