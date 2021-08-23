# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PersonHistory(models.Model):
    _inherit = 'clv.person.history'

    person_id = fields.Many2one(
        comodel_name='clv.person',
        string='Person',
        ondelete='restrict'
    )

    responsible_id = fields.Many2one(
        comodel_name='clv.person',
        string='Responsible',
        ondelete='restrict'
    )
    caregiver_id = fields.Many2one(
        comodel_name='clv.person',
        string='Caregiver',
        ondelete='restrict'
    )


class Person(models.Model):
    _inherit = 'clv.person'

    person_history_ids = fields.One2many(
        comodel_name='clv.person.history',
        inverse_name='person_id',
        string='Persons (History)'
    )
    count_person_histories = fields.Integer(
        string='Persons (History) (count)',
        compute='_compute_count_person_histories',
    )

    @api.depends('person_history_ids')
    def _compute_count_person_histories(self):
        for r in self:
            r.count_person_histories = len(r.person_history_ids)
