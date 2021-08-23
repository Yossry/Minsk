# -*- coding: utf-8 -*-
""" init object """
from odoo import fields, models, api, _ ,tools, SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from datetime import datetime , date ,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from odoo.fields import Datetime as fieldsDatetime
import calendar
from odoo import http
from odoo.http import request
from odoo import tools

import logging

LOGGER = logging.getLogger(__name__)

class InvoiceSelectionWizard(models.TransientModel):
    _name = 'invoice.selection.wizard'
    _description = 'Invoice Selection Wizard'

    invoice_ids = fields.Many2many(comodel_name="account.invoice")
    partner_id = fields.Many2one(comodel_name="res.partner")
    invoice_type = fields.Selection(default="out_invoice", selection=[('out_invoice', 'Customer Invoice'), ('out_refund', 'Customer Credit Note'), ], required=False, )

    @api.model
    def default_get(self, fields_list):
        group_id = self._context.get('active_id')
        account_invoice_group = self.env['account.invoice.group'].browse(group_id)
        res = super(InvoiceSelectionWizard,self).default_get(fields_list)
        res['invoice_ids'] = account_invoice_group.invoice_ids.ids
        res['partner_id'] = account_invoice_group.partner_id.id
        res['invoice_type'] = account_invoice_group.invoice_type
        return res

    def action_confirm(self):
        group_id = self._context.get('active_id')
        account_invoice_group = self.env['account.invoice.group'].browse(group_id)
        account_invoice_group.write({'invoice_ids': [(6, 0, self.invoice_ids.ids)]})

