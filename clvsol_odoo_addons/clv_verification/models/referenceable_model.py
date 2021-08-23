# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class VerificationBatchMember(models.Model):
    _name = "clv.verification.batch.member"
    _inherit = 'clv.verification.batch.member', 'clv.abstract.reference'
