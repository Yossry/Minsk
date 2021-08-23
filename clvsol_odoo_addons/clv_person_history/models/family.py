# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Family(models.Model):
    _inherit = 'clv.family'

    person_history_ids = fields.One2many(
        comodel_name='clv.person.history',
        inverse_name='ref_family_id',
        string='Persons (History)'
    )
    count_person_histories = fields.Integer(
        string='Persons (History) (count)',
        compute='_compute_count_person_historiess',
    )

    @api.depends('person_history_ids')
    def _compute_count_person_historiess(self):
        for r in self:
            r.count_person_histories = len(r.person_history_ids)


class PersonHistory(models.Model):
    _inherit = 'clv.person.history'

    ref_family_id = fields.Many2one(
        comodel_name='clv.family',
        string='Family',
        ondelete='restrict'
    )
