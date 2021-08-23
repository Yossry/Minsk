# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StreetCode(models.Model):
    _name = 'street.code'
    _description = 'Street Code'
    _rec_name = 'name'

    @api.multi
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for post in self:
            result.append((post.id, '%s %s' % (post.code, post.name)))
        return result

    code = fields.Char(required=True)
    name = fields.Char(string='Description', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'street.code'))
