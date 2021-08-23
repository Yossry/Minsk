# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

# from odoo import api, fields, models
from odoo import api, models

_logger = logging.getLogger(__name__)


class PersonSelGroupSetUp(models.TransientModel):
    _description = 'Person Sel Group SetUp'
    _name = 'clv.person_sel.group.setup'

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_person_sel_group_setup(self):
        self.ensure_one()

        # person_available_states = ['available', 'waiting', 'selected', 'unselected']
        person_available_states = ['available', 'waiting', 'selected']
        person_selected_states = ['selected']

        PersonSelGroup = self.env['clv.person_sel.group']
        Person = self.env['clv.person']
        PersonCategory = self.env['clv.person.category']

        PersonSelDistrict = self.env['clv.person_sel.district']
        districts = PersonSelDistrict.search([])

        PersonSelAgeGroup = self.env['clv.person_sel.age_group']
        age_groups = PersonSelAgeGroup.search([])

        for district in districts:

            for age_group in age_groups:

                name = district.name + ' - ' + age_group.name

                _logger.info(u'%s %s', '>>>>>', name)

                person_sel_group = PersonSelGroup.search([
                    ('name', '=', name),
                ])

                if person_sel_group.id is False:

                    values = {
                        'name': name,
                        # 'code': code,
                        'district_id': district.id,
                        'age_group_id': age_group.id,
                    }
                    person_sel_group = PersonSelGroup.create(values)

                persons = Person.search([
                    ('state', 'in', person_available_states),
                    ('age_reference_years', '>=', age_group.min_age),
                    ('age_reference_years', '<=', age_group.max_age),
                ])
                count = 0
                for person in persons:
                    category_id = PersonCategory.search([
                        ('name', '=', age_group.person_category_ids.name),
                    ]).id
                    if (person.category_ids.id == category_id) and \
                       (person.ref_address_id.district == district.name):
                        count += 1
                person_sel_group.available_persons = count

                persons = Person.search([
                    ('state', 'in', person_selected_states),
                    ('age_reference_years', '>=', age_group.min_age),
                    ('age_reference_years', '<=', age_group.max_age),
                ])
                count = 0
                for person in persons:
                    category_id = PersonCategory.search([
                        ('name', '=', age_group.person_category_ids.name),
                    ]).id
                    if (person.category_ids.id == category_id) and \
                       (person.ref_address_id.district == district.name):
                        count += 1
                person_sel_group.selected_persons = count

        return True
