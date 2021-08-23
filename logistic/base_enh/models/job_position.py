# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JobPosition(models.Model):
    _name = 'job.position'
    _description = "JobPosition"
    
    name = fields.Char('Name')
    
