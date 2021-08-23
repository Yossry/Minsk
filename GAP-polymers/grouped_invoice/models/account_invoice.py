# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _

import logging

LOGGER = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_invoice_group_id = fields.Many2one(comodel_name="account.invoice.group", string="Group")
    group_state = fields.Selection(string="Group State",related='account_invoice_group_id.state')

    @api.onchange('partner_id')
    def onchage_partner_group(self):
        self.update({'account_invoice_group_id': None})
