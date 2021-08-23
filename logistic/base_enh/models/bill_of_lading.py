# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AgreementMethod(models.Model):
    _name = 'bill.of.lading'
    _description = "AgreementMethod"
    
    shipping_line_id = fields.Many2one('line.cost')
    bill_lading_no = fields.Char (string='Bill Of Lading No.')
    shipper_id = fields.Many2one('res.partner', string='Shipper')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    first_notify_id = fields.Many2one('res.partner', string='First Notify Party')
    add_notify_id = fields.Many2one('res.partner', string='Additional Notify')
    booking_no = fields.Char(string='Booking No')
    contract_no = fields.Char(string='Contract No')
    port_loading_id = fields.Many2one('port', string="POL")
    port_dest_id = fields.Many2one('port', string="POD")
    vessel_id = fields.Many2one('vessel')
    voyage_id = fields.Many2one('voyages.detail')
    contract_no = fields.Char(string='Contract No')
    commodity_ids = fields.Many2many('commodity')
    place_of_loading = fields.Char(string='Place of Loading')
    place_of_receipt = fields.Char(string='Place of Receipt')
    
    
class ExternalBillOfLoading(models.Model):
    _name = 'external.bill.of.lading'
    _description = "ExternalBillOfLoading"
    
    shipping_line_id = fields.Many2one('line.cost')
    bill_lading_no = fields.Char (string='Bill Of Lading No.')
    shipper_id = fields.Many2one('res.partner', string='Shipper')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    first_notify_id = fields.Many2one('res.partner', string='First Notify Party')
    add_notify_id = fields.Many2one('res.partner', string='Additional Notify')
    booking_no = fields.Char(string='Booking No')
    contract_no = fields.Char(string='Contract No')
    port_loading_id = fields.Many2one('port', string="POL")
    port_dest_id = fields.Many2one('port', string="POD")
    vessel_id = fields.Many2one('vessel')
    voyage_id = fields.Many2one('voyages.detail')
    contract_no = fields.Char(string='Contract No')
    commodity_ids = fields.Many2many('commodity')
    place_of_loading = fields.Char(string='Place of Loading')
    place_of_receipt = fields.Char(string='Place of Receipt')
    
    
    