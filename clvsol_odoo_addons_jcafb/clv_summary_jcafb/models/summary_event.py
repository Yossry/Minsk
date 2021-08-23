# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryEvent(models.Model):
    _description = 'Summary Event'
    _name = 'clv.summary.event'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    event_id = fields.Many2one(
        comodel_name='clv.event',
        string='Event',
        ondelete='cascade'
    )
    event_global_tag_ids = fields.Many2many(
        string='Event Global Tags',
        related='event_id.global_tag_ids',
        store=False
    )
    event_category_ids = fields.Many2many(
        string='Event Categories',
        related='event_id.category_ids',
        store=False
    )
    event_state = fields.Selection(
        string='Event State',
        related='event_id.state',
        store=False
    )
    event_phase_id = fields.Many2one(
        string='Event Phase',
        related='event_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_event_ids = fields.One2many(
        comodel_name='clv.summary.event',
        inverse_name='summary_id',
        string='Events'
    )
