# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class PlaceOfDelivery(models.Model):
    _name = 'delivery.place'
    _rec_name = 'zip'
    _description = "PlaceOfDelivery"
    
    zip = fields.Integer('ZIP Code',required=True)
    country_id = fields.Many2one('res.country',required=True)
    city_id = fields.Many2one('res.city',required=True)
    state_id = fields.Many2one('res.country.state',required=True)
    address = fields.Text('Address',required=True)
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s | %s'%(record.zip,record.address)))

        return result
    
    

class PlaceOfLoading(models.Model):
    _name = 'loading.place'
    _rec_name = 'zip'
    _description = "PlaceOfLoading"
    
    zip = fields.Integer('ZIP Code',required=True)
    country_id = fields.Many2one('res.country',required=True)
    city_id = fields.Many2one('res.city',required=True)
    state_id = fields.Many2one('res.country.state',required=False)
    address = fields.Text('Address',required=True)
    
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s | %s'%(record.zip,record.address)))
        return result   

