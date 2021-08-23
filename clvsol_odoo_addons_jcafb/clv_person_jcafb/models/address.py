# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Person(models.Model):
    _inherit = 'clv.person'

    ref_address_state = fields.Selection(string='Address State', related='ref_address_id.state', store=False)
