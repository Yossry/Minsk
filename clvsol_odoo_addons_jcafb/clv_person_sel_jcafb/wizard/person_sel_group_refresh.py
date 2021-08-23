# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PersonSelGroupRefresh(models.TransientModel):
    _description = 'Person Sel Group Refresh'
    _name = 'clv.person_sel.group.refresh'

    def _default_group_ids(self):
        return self._context.get('active_ids')
    group_ids = fields.Many2many(
        comodel_name='clv.person_sel.group',
        relation='clv_person_sel_group_refresh_rel',
        string='Person Selection Groups',
        domain=['|', ('active', '=', False), ('active', '=', True)],
        default=_default_group_ids
    )

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
    def do_person_sel_group_refresh(self):
        self.ensure_one()

        # person_available_states = ['available', 'waiting', 'selected', 'unselected']
        person_available_states = ['available', 'waiting', 'selected']
        person_selected_states = ['selected']

        Person = self.env['clv.person']
        PersonCategory = self.env['clv.person.category']

        for group in self.group_ids:

            _logger.info(u'%s %s', '>>>>>', group.name)

            persons = Person.search([
                ('state', 'in', person_available_states),
                ('age_reference_years', '>=', group.age_group_id.min_age),
                ('age_reference_years', '<=', group.age_group_id.max_age),
            ])
            count = 0
            for person in persons:
                category_id = PersonCategory.search([
                    ('name', '=', group.age_group_id.person_category_ids.name),
                ]).id
                if (person.category_ids.id == category_id) and \
                   (person.ref_address_id.district == group.district_id.name):
                    count += 1
            group.available_persons = count

            persons = Person.search([
                ('state', 'in', person_selected_states),
                ('age_reference_years', '>=', group.age_group_id.min_age),
                ('age_reference_years', '<=', group.age_group_id.max_age),
            ])
            count = 0
            for person in persons:
                category_id = PersonCategory.search([
                    ('name', '=', group.age_group_id.person_category_ids.name),
                ]).id
                if (person.category_ids.id == category_id) and \
                   (person.ref_address_id.district == group.district_id.name):
                    count += 1
            group.selected_persons = count

        return True

    @api.multi
    def do_populate_all(self):
        self.ensure_one()

        PersonSelGroup = self.env['clv.person_sel.group']
        person_sel_groups = PersonSelGroup.search([])

        self.group_ids = person_sel_groups

        return self._reopen_form()
