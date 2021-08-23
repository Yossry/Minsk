# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VerificationBatchMember(models.Model):
    _description = 'Verification Batch Member'
    _name = 'clv.verification.batch.member'
    _order = "sequence"

    verification_batch_id = fields.Many2one(
        comodel_name='clv.verification.batch',
        string='Verification Batch ',
        required=False
    )

    notes = fields.Text(string='Notes')

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )


class VerificationBatch(models.Model):
    _inherit = 'clv.verification.batch'

    verification_batch_member_ids = fields.One2many(
        comodel_name='clv.verification.batch.member',
        inverse_name='verification_batch_id',
        string='Members',
        readonly=False
    )
    count_verification_batch_members = fields.Integer(
        string='Members (count)',
        compute='_compute_count_verification_batch_members',
        store=False
    )

    @api.depends('verification_batch_member_ids')
    def _compute_count_verification_batch_members(self):
        for r in self:
            r.count_verification_batch_members = len(r.verification_batch_member_ids)
