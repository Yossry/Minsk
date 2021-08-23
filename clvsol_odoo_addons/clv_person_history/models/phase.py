# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    person_ids = fields.One2many(
        comodel_name='clv.person',
        inverse_name='phase_id',
        string='Persons',
        readonly=True
    )
    count_persons = fields.Integer(
        string='Persons (count)',
        compute='_compute_person_ids_and_count',
    )

    @api.multi
    def _compute_person_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            persons = self.env['clv.person'].search(search_domain)

            record.count_persons = len(persons)
            record.person_ids = [(6, 0, persons.ids)]

    person_history_ids = fields.One2many(
        comodel_name='clv.person.history',
        inverse_name='phase_id',
        string='Persons (History)',
        readonly=True
    )
    count_person_histories = fields.Integer(
        string='Persons (History) (count)',
        compute='_compute_person_history_ids_and_count',
    )

    @api.multi
    def _compute_person_history_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            person_histories = self.env['clv.person.history'].search(search_domain)

            record.count_person_histories = len(person_histories)
            record.person_history_ids = [(6, 0, person_histories.ids)]


class Person(models.Model):
    _inherit = 'clv.person'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )


class PersonHistory(models.Model):
    _inherit = 'clv.person.history'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )
