# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
import logging
import pytz
import time
import babel

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipper = fields.Boolean('Shipper')
    consignee = fields.Boolean('Consignee')
    agent = fields.Boolean('Agent')

class CustomerInvoice(models.Model):
    _inherit = 'account.invoice'

    freight_operation_id = fields.Many2one('freight.operation', string='Freight operation')

class ShipmentStage(models.Model):
    _name = 'shipment.stage'
    _description = 'shipment Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

class FreightOperation(models.Model):
    _name = 'freight.operation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Freight Operation'

    def _get_default_stage_id(self):
        return self.env['shipment.stage'].search([], order='sequence', limit=1)

    color = fields.Integer('Color')
    stage_id = fields.Many2one('shipment.stage', 'Stage',default=_get_default_stage_id, group_expand='_read_group_stage_ids')
    name = fields.Char(string='Name')
    direction = fields.Selection(([('import','Import'),('export','Export')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper')
    consignee_id = fields.Many2one('res.partner', 'Consignee')
    source_location_id = fields.Many2one('freight.port', 'Source Location', index=True, required=True)
    destination_location_id = fields.Many2one('freight.port', 'Destination Location', index=True, required=True)
    obl = fields.Char('OBL', help='Original Bill Of Landing')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_number = fields.Char('Trucker No')
    agent_id = fields.Many2one('res.partner', 'Agent')
    operator_id = fields.Many2one('res.users', 'User')
    freight_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Freight PC")
    other_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Other PC")
    notes = fields.Text('Notes')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    dangerous_goods_notes = fields.Text('Dangerous Goods Info')
    move_type = fields.Many2one('freight.move.type', 'Move Type')
    tracking_number = fields.Char('Tracking Number')
    declaration_number = fields.Char('Declaration Number')
    declaration_date = fields.Date('Declaration Date')
    custom_clearnce_date = fields.Datetime('Customs Clearance Date')
    freight_orders = fields.One2many('freight.order', 'shipment_id')
    freight_packages = fields.One2many('freight.package.line', 'shipment_id')
    freight_services = fields.One2many('freight.service', 'shipment_id')
    incoterm = fields.Many2one('freight.incoterms','Incoterm')
    freight_routes = fields.One2many('freight.route', 'shipment_id')
    parent_id = fields.Many2one('freight.operation', 'Parent')
    shipments_ids = fields.One2many('freight.operation', 'parent_id')
    service_count = fields.Float('Services Count', compute='_compute_invoice')
    invoice_count = fields.Float('Services Count', compute='_compute_invoice')
    vendor_bill_count = fields.Float('Services Count', compute='_compute_invoice')
    total_invoiced = fields.Float('Total Invoiced(Receivables', compute='compute_total_amount')
    total_bills = fields.Float('Total Bills(Payables)', compute='compute_total_amount')
    margin = fields.Float("Margin", compute='compute_total_amount')
    invoice_residual = fields.Float('Invoice Residual',compute='compute_total_amount')
    bills_residual = fields.Float('Bills Residual', compute='compute_total_amount')
    invoice_paid_amount = fields.Float('Invoice', compute='compute_total_amount')
    bills_paid_amount = fields.Float('Bills', compute='compute_total_amount')
    actual_margin = fields.Float('Actual Margin', compute='compute_total_amount')

    @api.depends('freight_services')
    def compute_total_amount(self):
        for order in self:
            invoices = self.env['account.invoice'].sudo().search([('freight_operation_id', '=', order.id), ('type', '=', 'out_invoice')])
            invoice_amount = 0.0
            bill_amount = 0.0
            invoice_residual = 0.0
            bills_residual = 0.0
            for invoice in invoices:
                invoice_amount+=invoice.amount_total
                invoice_residual+= invoice.residual

            bills = self.env['account.invoice'].sudo().search([('freight_operation_id', '=', order.id), ('type', '=', 'in_invoice')])
            for bill in bills:
                bill_amount+=bill.amount_total
                if bill.state != 'draft':
                    bills_residual+= bill.residual

            order.total_invoiced = invoice_amount
            order.total_bills = bill_amount
            order.margin =  invoice_amount - bill_amount
            order.invoice_residual = invoice_residual
            order.bills_residual = bills_residual

            payment_total = 0.0
            for invoice in invoices:
                for payment in invoice.payment_ids:
                    payment_total+=payment.amount
            order.invoice_paid_amount = payment_total
            bill_payment_total = 0.0
            for bill_payment in invoices:
                for payment in bill_payment.payment_ids:
                    bill_payment_total+=payment.amount
            order.bills_paid_amount = bill_payment_total
            order.actual_margin =order.invoice_paid_amount - order.bills_paid_amount

    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['shipment.stage'].search([])
        return stage_ids

    @api.depends('freight_services')
    def _compute_invoice(self):
        for order in self:
            order.service_count = len(order.freight_services)
            order.invoice_count = self.env['account.invoice'].sudo().search_count([('freight_operation_id','=', order.id),('type','=', 'out_invoice')])
            order.vendor_bill_count  = self.env['account.invoice'].sudo().search_count([('freight_operation_id','=', order.id),('type','=', 'in_invoice')])

    @api.multi
    def button_services(self):
        views = [(self.env.ref('freight.view_freight_service_tree').id, 'tree'),
                 (self.env.ref('freight.view_freight_service_form').id, 'form')]
        return {
            'name': _('Services'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'freight.service',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.freight_services])],
        }

    @api.multi
    def button_customer_invoices(self):
        invoices = self.env['account.invoice'].sudo().search(
            [('freight_operation_id', '=', self.id), ('type', '=', 'out_invoice')])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def button_vendor_bills(self):
        invoices = self.env['account.invoice'].sudo().search(
            [('freight_operation_id', '=', self.id), ('type', '=', 'in_invoice')])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            if values.get('operation') == 'master':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.master') or _('New')
            elif values.get('operation') == 'house':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.house') or _('New')
            elif values.get('operation') == 'direct':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.direct') or _('New')
        id = super(FreightOperation, self).create(values)
        if id.transport == 'air':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'mawb_no': id.mawb_no,
                                              'airline_id': id.airline_id.id,
                                              'flight_no': id.flight_no,
                                              'shipment_id': id.id})
        if id.transport == 'ocean':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'shipping_line_id': id.shipping_line_id.id,
                                              'vessel_id': id.vessel_id.id,
                                              'obl': id.obl,
                                              'shipment_id': id.id})
        if id.transport == 'land':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'truck_ref': id.truck_ref.id,
                                              'trucker': id.trucker.id,
                                              'trucker_number': id.trucker_number,
                                              'shipment_id': id.id})
        return id

    @api.depends('transport')
    @api.onchange('source_location_id')
    def onchange_source_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'source_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'source_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'source_location_id': [('land', '=', True)]}}

    @api.depends('transport')
    @api.onchange('destination_location_id')
    def onchange_destination_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'destination_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'destination_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'destination_location_id': [('land', '=', True)]}}

    @api.multi
    def generate_from_the_orders(self):
        for line in self:
            packages = []
            for order in line.freight_orders:
                packages.append((0, 0, {'name': order.name,
                                        'package':order.package.id,
                                        'qty': order.qty,
                                        'volume': order.volume,
                                        'gross_weight': order.gross_weight,
                                        'shipment_id':line.id}))
            self.freight_packages.unlink()
            self.write({'freight_packages':packages})

class FreightTrucker(models.Model):
    _name = 'freight.trucker'

    name = fields.Char(string='Name')

class FreightPackageLine(models.Model):
    _name = 'freight.package.line'

    name = fields.Char(string='Description', required=True)
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity', required=True)
    harmonize = fields.Char('Harmonize')
    temperature = fields.Char('Temperature')
    vgm = fields.Char('VGM', help='Verified gross mass')
    carrier_seal = fields.Char('Carrier Seal')
    shipper_seal = fields.Char('Shipper Seal')
    reference = fields.Char('Reference')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    class_number = fields.Char('Class Number')
    un_number = fields.Char('UN Number', help='UN numbers are four-digit numbers that identify hazardous materials, and articles in the framework of international transport')
    Package_group = fields.Char('Packaging Group:')
    imdg_code = fields.Char('IMDG Code', help='International Maritime Dangerous Goods Code')
    flash_point = fields.Char('Flash Point')
    material_description = fields.Text('Material Description')
    freight_item_lines = fields.One2many('freight.item.line', 'package_line_id')
    route_id = fields.Many2one('freight.route', 'Route')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightItemLine(models.Model):
    _name = 'freight.item.line'

    name = fields.Char(string='Description')
    package_line_id = fields.Many2one('freight.package.line', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package')
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.package_line_id.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightOrder(models.Model):
    _name = 'freight.order'

    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    name = fields.Char(string='Description', required=True)
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightService(models.Model):
    _name = 'freight.service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    qty = fields.Float('Quantity')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    route_id = fields.Many2one('freight.route', 'Route')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID', related='route_id.shipment_id')
    customer_invoice = fields.Many2one('account.invoice')
    vendor_invoice = fields.Many2one('account.invoice')
    invoiced = fields.Boolean('Invoiced')
    vendor_invoiced = fields.Boolean('Vendor Invoiced')

class FreightRoute(models.Model):
    _name = 'freight.route'

    name=fields.Char('Description', compute='compute_name')
    type = fields.Selection([('pickup', 'Pickup'), ('oncarriage', 'On Carriage'), ('precarriage', 'Pre Carriage'),('delivery', 'Delivery')], string='Type')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection([('air','Air'),('ocean','Ocean'),('land','Land')], string='Transport')
    ocean_shipment_type = fields.Selection([('fcl','FCL'),('lcl','LCL')], string='Shipment Type')
    inland_shipment_type = fields.Selection([('ftl','FTL'),('ltl','LTL')], string='Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper')
    consignee_id = fields.Many2one('res.partner', 'Consignee')
    source_location_id = fields.Many2one('freight.port', 'Source Location')
    destination_location_id = fields.Many2one('freight.port', 'Destination Location')
    obl = fields.Char('OBL', help='Original Bill Of Lading')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_number = fields.Many2one('freight.trucker', 'Trucker No')
    etd = fields.Datetime('ETD')
    eta = fields.Datetime('ETA')
    atd = fields.Datetime('ATD')
    ata = fields.Datetime('ATA')
    package_ids = fields.One2many('freight.package.line', 'route_id')
    freight_services = fields.One2many('freight.service', 'route_id')
    main_carriage = fields.Boolean('Main Carriage')

    @api.model
    def create(self, values):
        id = super(FreightRoute, self).create(values)
        id.freight_services.write({'shipment_id':id.shipment_id})
        return id

    @api.multi
    def compute_name(self):
        for line in self:
            if line.main_carriage:
                line.name = 'Main carriage'
            elif line.type:
                line.name = line.type

    @api.onchange('type')
    def onchange_type(self):
        for line in self:
            if line.type == 'precarriage':
                line.destination_location_id = line.shipment_id.source_location_id
            if line.type == 'oncarriage':
                line.source_location_id = line.shipment_id.destination_location_id

class FreightRouteService(models.Model):
    _name = 'freight.route.service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    partner_id = fields.Many2one('res.partner', 'Vendor')

class FreightPort(models.Model):
    _name = 'freight.port'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    country = fields.Many2one('res.country', 'Country')
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=', country)]")
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')
    active = fields.Boolean(default=True, string='Active')

class FreightVessel(models.Model):
    _name = 'freight.vessel'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    global_zone = fields.Char(string='Global Zone')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightAirline(models.Model):
    _name = 'freight.airline'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    icao = fields.Char(string='ICAO')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightIncoterms(models.Model):
    _name = 'freight.incoterms'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name',  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    active = fields.Boolean(default=True, string='Active')

class FreightPackage(models.Model):
    _name = 'freight.package'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    container = fields.Boolean('Is Container?')
    refrigerated = fields.Boolean('Refrigerated')
    active = fields.Boolean(default=True, string='Active')
    size = fields.Float('Size')
    volume = fields.Float('Volume')
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')

class FreightMoveType(models.Model):
    _name = 'freight.move.type'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')