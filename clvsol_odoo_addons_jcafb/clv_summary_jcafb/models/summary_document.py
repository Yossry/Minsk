# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryDocument(models.Model):
    _description = 'Summary Document'
    _name = 'clv.summary.document'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    document_id = fields.Many2one(
        comodel_name='clv.document',
        string='Document',
        ondelete='cascade'
    )
    document_global_tag_ids = fields.Many2many(
        string='Document Global Tags',
        related='document_id.global_tag_ids',
        store=False
    )
    document_category_ids = fields.Many2many(
        string='Document Categories',
        related='document_id.category_ids',
        store=False
    )
    document_state = fields.Selection(
        string='Document State',
        related='document_id.state',
        store=False
    )
    document_phase_id = fields.Many2one(
        string='Document Phase',
        related='document_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_document_ids = fields.One2many(
        comodel_name='clv.summary.document',
        inverse_name='summary_id',
        string='Documents'
    )
