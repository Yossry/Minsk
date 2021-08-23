# -*- coding: utf-8 -*-

from odoo import fields, models


class CiiuValue(models.Model):
    _name = 'ciiu.value'
    _description = 'CIIU Optional Value'

    code = fields.Char(required=True)
    name = fields.Char(string='Description', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'ciiu.value'))

# class ciiu_contacts_values(models.Model):
#     _name = 'ciiu.contacts.values'
#
#
#     contact_id = fields.Integer()
#     ciiu_id = fields.Integer()
#     id = fields.Integer()
