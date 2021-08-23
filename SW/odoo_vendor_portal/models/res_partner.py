# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_reg = fields.Boolean(
        default=False,
        string="Vendor Registered")
