# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    survey_ids = fields.One2many(
        comodel_name='survey.survey',
        inverse_name='phase_id',
        string='Surveys',
        readonly=True
    )
    count_surveys = fields.Integer(
        string='Surveys (count)',
        compute='_compute_survey_ids_and_count',
    )

    @api.multi
    def _compute_survey_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            surveys = self.env['survey.survey'].search(search_domain)

            record.count_surveys = len(surveys)
            record.survey_ids = [(6, 0, surveys.ids)]


class Survey(models.Model):
    _inherit = 'survey.survey'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )
