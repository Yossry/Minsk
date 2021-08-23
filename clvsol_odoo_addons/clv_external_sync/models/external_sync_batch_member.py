# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ExternalSyncBatchMember(models.Model):
    _description = 'External Sync Batch Member'
    _name = 'clv.external_sync.batch.member'
    _order = "sequence"

    external_sync_batch_id = fields.Many2one(
        comodel_name='clv.external_sync.batch',
        string='External Sync Batch ',
        required=False
    )

    notes = fields.Text(string='Notes')

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )


class ExternalSyncBatch(models.Model):
    _inherit = 'clv.external_sync.batch'

    external_sync_batch_member_ids = fields.One2many(
        comodel_name='clv.external_sync.batch.member',
        inverse_name='external_sync_batch_id',
        string='Members',
        readonly=False
    )
    count_external_sync_batch_members = fields.Integer(
        string='Number of Members',
        compute='_compute_count_external_sync_batch_members',
        store=False
    )

    @api.depends('external_sync_batch_member_ids')
    def _compute_count_external_sync_batch_members(self):
        for r in self:
            r.count_external_sync_batch_members = len(r.external_sync_batch_member_ids)
