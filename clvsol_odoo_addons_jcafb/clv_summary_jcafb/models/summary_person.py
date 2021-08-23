# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SummaryPerson(models.Model):
    _description = 'Summary Person'
    _name = 'clv.summary.person'

    summary_id = fields.Many2one(
        comodel_name='clv.summary',
        string='Summary',
        index=True,
        ondelete='cascade'
    )
    person_id = fields.Many2one(
        comodel_name='clv.person',
        string='Person',
        ondelete='cascade'
    )
    person_gender = fields.Selection(
        string='Person Gender',
        related='person_id.gender',
        store=False
    )
    person_birthday = fields.Date(
        string='Person Date of Birth',
        related='person_id.birthday',
        store=False
    )
    person_global_tag_ids = fields.Many2many(
        string='Person Global Tags',
        related='person_id.global_tag_ids',
        store=False
    )
    person_category_ids = fields.Many2many(
        string='Person Categories',
        related='person_id.category_ids',
        store=False
    )
    person_state = fields.Selection(
        string='Person State',
        related='person_id.state',
        store=False
    )
    person_phase_id = fields.Many2one(
        string='Person Phase',
        related='person_id.phase_id',
        store=False
    )


class Summary(models.Model):
    _inherit = "clv.summary"

    summary_person_ids = fields.One2many(
        comodel_name='clv.summary.person',
        inverse_name='summary_id',
        string='Persons'
    )
