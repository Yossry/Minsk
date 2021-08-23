# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InsuranceType(models.Model):
    _name = 'insurance.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "InsuranceType"
    
    name = fields.Char('Name',required=True)
    note = fields.Char('Note')
    active=fields.Boolean(default=True)
