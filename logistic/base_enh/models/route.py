# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Route(models.Model):
    _name = 'route'
    _description = "Route"
    
    job_route_id = fields.Many2one ('job')
    shipment_method = fields.Selection([('clearance', 'Clearance'), 
                                        ('sea_freight', 'Sea freight'), 
                                        ('land_freight', 'Land Freight'), 
                                        ('air_freight', 'Air Freight')],
                                        string="Shipment Method")
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one('res.country.state', string="State")
    city_id = fields.Many2one('res.city', string="City")
    place_id = fields.Many2one('res.place', string="Place")
    sea_port_id = fields.Many2one('port', string="Sea Port")
    air_port_id = fields.Many2one('port', string="Air Port")
    place_of_port_id = fields.Many2one('res.place',string="Terminal")
    custom_point_id = fields.Many2one('res.partner', string="Customs Point")
    depot_id = fields.Many2one('res.partner', string="Depot")
    border_point_id = fields.Many2one('res.partner', string="Border Point")
    dry_port_id = fields.Many2one('port', string="Dry Port")
    