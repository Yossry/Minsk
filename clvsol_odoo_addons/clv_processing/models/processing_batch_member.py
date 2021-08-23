# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcessingBatchMember(models.Model):
    _description = 'Processing Batch Member'
    _name = 'clv.processing.batch.member'
    _order = "sequence"

    processing_batch_id = fields.Many2one(
        comodel_name='clv.processing.batch',
        string='Processing Batch ',
        required=False
    )

    notes = fields.Text(string='Notes')

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )


class ProcessingBatch(models.Model):
    _inherit = 'clv.processing.batch'

    processing_batch_member_ids = fields.One2many(
        comodel_name='clv.processing.batch.member',
        inverse_name='processing_batch_id',
        string='Members',
        readonly=False
    )
    count_processing_batch_members = fields.Integer(
        string='Members (count)',
        compute='_compute_count_processing_batch_members',
        store=False
    )

    @api.depends('processing_batch_member_ids')
    def _compute_count_processing_batch_members(self):
        for r in self:
            r.count_processing_batch_members = len(r.processing_batch_member_ids)
