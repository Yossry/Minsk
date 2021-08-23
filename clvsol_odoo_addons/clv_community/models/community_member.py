# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CommunityMember(models.Model):
    _description = 'Community Member'
    _name = 'clv.community.member'

    community_id = fields.Many2one(
        comodel_name='clv.community',
        string='Community',
        required=False
    )

    notes = fields.Text(string='Notes')


class Community(models.Model):
    _inherit = 'clv.community'

    community_member_ids = fields.One2many(
        comodel_name='clv.community.member',
        inverse_name='community_id',
        string='Members',
        readonly=True
    )
    count_community_members = fields.Integer(
        string='Number of Members',
        compute='_compute_count_community_members',
        store=False
    )

    @api.depends('community_member_ids')
    def _compute_count_community_members(self):
        for r in self:
            r.count_community_members = len(r.community_member_ids)
