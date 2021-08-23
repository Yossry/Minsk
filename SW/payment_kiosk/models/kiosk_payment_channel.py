# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_kiosk_partner = fields.Boolean()
    rate_ids = fields.One2many('kiosk.rates', 'payment_channel_id', string='Rate Details')
    kiosk_account_id = fields.Many2one('account.account', string='Bank Charge Account')


class KioskRates(models.Model):
    _inherit = 'kiosk.rates'

    payment_channel_id = fields.Many2one('account.journal')
