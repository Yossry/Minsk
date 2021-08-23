# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TerminalKiosk(models.Model):
    _name = 'kiosk.terminal'
    _description = 'Kiosk Terminal'
    _rec_name = 'reference'

    name = fields.Char(string="Kiosk Name")
    kiosk_id = fields.Char(string="Kiosk ID")
    reference = fields.Char(string='Reference/Code')
    start_date = fields.Datetime(string='Start Date')
    kiosk_location = fields.Char(string="Kiosk Location")
    kiosk_os = fields.Char(string="Kiosk OS")
    licence_Key = fields.Char(string="Licence Key")
    top_screen = fields.Char(string="Top Screen")
    lower_screen = fields.Char(string="Lower Screen")
    kiosk_nfc = fields.Char(string="NFC")
    kiosk_pos = fields.Char(string="POS")
    card_reader = fields.Char(string="Card Reader")
    printer_receipt = fields.Char(string="Receipt Printer")
    cash_acceptor = fields.Char(string="Cash Acceptor")
    finger_print = fields.Boolean('Finger Print', default=False, help="If Kiosk have Finger Print Option")
    barcode_reader = fields.Boolean('Barcode Reader', default=False, help="If Kiosk have Barcode Reader Option")
    router = fields.Char(string="Router")
    sim_card = fields.Char(string="Sim Card")
    amount = fields.Integer()
    state = fields.Selection([
        ('pending', 'Non Active'),
        ('authorized', 'Authorized')],
        string='Kiosk Status', default='pending')
    amount_limit = fields.Integer(string="Amount Limit")
