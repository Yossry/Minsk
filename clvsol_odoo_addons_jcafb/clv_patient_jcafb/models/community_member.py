# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = 'clv.patient'

    community_member_ids = fields.One2many(
        string='Community Members',
        comodel_name='clv.community.member',
        compute='_compute_community_member_ids_and_count',
    )
    count_communities = fields.Integer(
        string='Communities',
        compute='_compute_community_member_ids_and_count',
    )

    @api.multi
    def _compute_community_member_ids_and_count(self):
        for record in self:
            community_members = self.env['clv.community.member'].search([
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ])
            record.count_communities = len(community_members)
            record.community_member_ids = [(6, 0, community_members.ids)]
