# -*- coding: utf-8 -*-

from odoo import models, fields, api


class vessel(models.Model):
    _name = 'vessel'
    _inherit = [ 'mail.thread']
    _description = "vessel"
    
    sea_line_id = fields.Many2one('res.partner',string="Shipping",domain=[('is_sea_line','=',True)],required=True)
    name = fields.Char('Name',required=True)
    country_id = fields.Many2one('res.country',string="Flag")
    image = fields.Binary(attachment=True,related="country_id.image",readonly=True)
    Home_port_id = fields.Many2one('port',string="Home Port")
    build = fields.Selection([(year,year) for year in range(1950,2051)])
    code = fields.Char('Code')
    note = fields.Char('Notes')
    imo_number  = fields.Char('Imo Number')
    voyages_ids = fields.One2many("voyages.detail",'vessel_id')
    
class VoyagesDetail(models.Model):
    _name = "voyages.detail"
    _rec_name = "voyage_number"
    _description = "VoyagesDetail"
    
    vessel_id = fields.Many2one('vessel')
    voyage_number  = fields.Char('Voyage Number')
    etd_date = fields.Date('ETD Ddate')
    eta_date = fields.Date('ETA Ddate')
    