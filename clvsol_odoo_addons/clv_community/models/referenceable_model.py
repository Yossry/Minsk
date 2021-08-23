# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CommunityMember(models.Model):
    _name = "clv.community.member"
    _inherit = 'clv.community.member', 'clv.abstract.reference'
