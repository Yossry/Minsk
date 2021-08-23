# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from functools import reduce

from odoo import api, fields, models

from time import time

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


def format_number(value):

    if value == 0:
        value_str = False
    else:
        value_str = str(value)
        while len(value_str) < 3:
            value_str = ' ' + value_str
    return value_str


class PersonSelSummarySetUp(models.TransientModel):
    _description = 'Person Sel Summary SetUp'
    _name = 'clv.person_sel.summary.setup'

    def _default_phase_id(self):
        phase_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_phase_id', '').strip())
        return phase_id
    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        default=_default_phase_id,
        ondelete='restrict'
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
    def do_person_sel_summary_setup(self):
        self.ensure_one()

        _logger.info(u'%s %s', '>>>>>', 'do_person_sel_summary_setup...')
        start = time()

        row_max = 18
        col_max = 64

        # person_available_states = ['available', 'waiting', 'selected', 'unselected']
        person_available_states = ['available', 'waiting', 'selected']
        person_selected_states = ['selected']

        addr_categories = [u'Zona Urbana', u'Zona Rural']
        person_categories = [u'Criança', u'Idoso', u'Gestante']

        matrix = [[False for col_nr in range(col_max + 1)] for row_nr in range(row_max + 1)]
        for row_nr in range(0, row_max + 1):
            for col_nr in range(1, col_max + 1):
                # matrix[row_nr][col_nr] = str(row_nr) + ',' + str(col_nr)
                pass

        AddressCategory = self.env['clv.address.category']
        PersonSelDistrict = self.env['clv.person_sel.district']
        PersonCategory = self.env['clv.person.category']
        Person = self.env['clv.person']
        PersonSelAgeGroup = self.env['clv.person_sel.age_group']
        PersonSelGroup = self.env['clv.person_sel.group']

        mark_str = '* '

        # *********************************************************************************
        #
        # Avalilable
        #
        # *********************************************************************************

        row_base_nr = 1
        col_base_nr = 1

        person_states = person_available_states

        row_nr, col_nr = row_base_nr - 1, col_base_nr
        matrix[row_nr][col_nr] = '(Available________)'

        addr_category_names = []
        district_names = []
        person_category_names = []
        age_group_names = []

        row_nr, col_nr = row_base_nr, col_base_nr + 2
        row_age_group = row_nr
        col_first_age_group = col_nr

        for person_category_name in person_categories:

            person_category_names.append(person_category_name)
            person_category = PersonCategory.search([
                ('name', '=', person_category_name),
            ])

            person_sel_age_groups = PersonSelAgeGroup.search([
                ('person_category_ids', '=', person_category.id),
            ])
            for person_sel_age_group in person_sel_age_groups:
                age_group_names.append(person_sel_age_group.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_age_group.name
                col_last_age_group = col_nr
                col_nr += 1

            matrix[row_nr][col_nr] = person_category.name
            col_last_age_group = col_nr
            col_nr += 1

            col_nr += 1

        col_total = col_nr

        row_nr, col_nr = row_base_nr + 2, col_base_nr
        row_first_district = row_nr
        col_district = col_nr

        for addr_category_name in addr_categories:

            addr_category_names.append(addr_category_name)
            addr_category = AddressCategory.search([
                ('name', '=', addr_category_name),
            ])

            person_sel_districts = PersonSelDistrict.search([
                ('addr_category_ids', '=', addr_category.id),
            ])
            for person_sel_district in person_sel_districts:
                district_names.append(person_sel_district.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_district.name
                row_last_district = row_nr
                row_nr += 1

            matrix[row_nr][col_nr] = addr_category.name
            row_last_district = row_nr
            row_nr += 1

            row_nr += 1

        row_total = row_nr

        matrix[row_total][col_base_nr] = 'Total'
        matrix[row_base_nr][col_total] = 'Total'

        for row_nr in range(row_first_district, row_last_district + 1):
            for col_nr in range(col_first_age_group, col_last_age_group + 1):
                _logger.info(u'%s %s', '>>>>>>>>>>', str(row_nr) + ',' + str(col_nr))
                if (matrix[row_nr][col_district] is not False) and \
                   (matrix[row_age_group][col_nr] is not False):
                    district = matrix[row_nr][col_district].replace(mark_str, '')
                    age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                    if (district in district_names) and \
                       (age_group in age_group_names):
                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                            ('age_reference_years', '>=', person_age_group.min_age),
                            ('age_reference_years', '<=', person_age_group.max_age),
                        ])

                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                     district, age_group, len(available_persons))

                        count = 0
                        for available_person in available_persons:
                            person_category_id = PersonCategory.search([
                                ('name', '=', person_age_group.person_category_ids.name),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.district == person_sel_district.name):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in addr_category_names) and \
                       (age_group in age_group_names):

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                            ('age_reference_years', '>=', person_age_group.min_age),
                            ('age_reference_years', '<=', person_age_group.max_age),
                        ])

                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                     district, age_group, len(available_persons))

                        count = 0
                        for available_person in available_persons:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            person_category_id = PersonCategory.search([
                                ('name', '=', person_age_group.person_category_ids.name),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.category_ids.id == addr_category_id):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in district_names) and \
                       (age_group in person_category_names):

                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                        ])

                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                     district, age_group, len(available_persons))

                        count = 0
                        for available_person in available_persons:
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.district == person_sel_district.name):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in addr_category_names) and \
                       (age_group in person_category_names):

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                        ])

                        _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                     district, age_group, len(available_persons))

                        count = 0
                        for available_person in available_persons:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.category_ids.id == addr_category_id):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

        for row_nr in range(row_first_district, row_last_district + 1):
            if (matrix[row_nr][col_district] is not False):
                district = matrix[row_nr][col_district].replace(mark_str, '')
                if district in district_names:
                    person_sel_district = PersonSelDistrict.search([
                        ('name', '=', district),
                    ])
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                 district, age_group, len(available_persons))

                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id is not False) and \
                           (available_person.ref_address_id.district == person_sel_district.name):
                            count += 1
                    matrix[row_nr][col_total] = format_number(count)
                if district in addr_category_names:
                    addr_category_id = AddressCategory.search([
                        ('name', '=', district),
                    ]).id
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                 district, age_group, len(available_persons))

                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id is not False) and \
                           (available_person.ref_address_id.category_ids.id == addr_category_id):
                            count += 1
                    matrix[row_nr][col_total] = format_number(count)

        for col_nr in range(col_first_age_group, col_last_age_group + 1):
            if (matrix[row_age_group][col_nr] is not False):
                age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                if age_group in age_group_names:
                    person_sel_age_group = PersonSelAgeGroup.search([
                        ('name', '=', age_group),
                    ])
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                        ('age_reference_years', '>=', person_sel_age_group.min_age),
                        ('age_reference_years', '<=', person_sel_age_group.max_age),
                    ])
                    person_category_id = PersonCategory.search([
                        ('name', '=', person_sel_age_group.person_category_ids.name),
                    ]).id

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                 district, age_group, len(available_persons))

                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id == person_category_id) and \
                           (available_person.ref_address_id.category_ids.id is not False):
                            count += 1
                    matrix[row_total][col_nr] = format_number(count)
                if age_group in person_category_names:
                    person_category_id = PersonCategory.search([
                        ('name', '=', age_group),
                    ]).id
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])

                    _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                                 district, age_group, len(available_persons))

                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id == person_category_id) and \
                           (available_person.ref_address_id.category_ids.id is not False):
                            count += 1
                    matrix[row_total][col_nr] = format_number(count)

        available_persons = Person.search([
            ('state', 'in', person_states),
            ('phase_id', '=', self.phase_id.id),
        ])

        _logger.info(u'%s %s %s %s', '>>>>>>>>>>>>>>>',
                     district, age_group, len(available_persons))

        count = 0
        for available_person in available_persons:
            if (available_person.category_ids.id is not False) and \
               (available_person.ref_address_id.category_ids.id is not False):
                count += 1
        matrix[row_total][col_total] = format_number(count)

        # *********************************************************************************
        #
        # Capacity
        #
        # *********************************************************************************

        row_base_nr = 1
        col_base_nr = col_total + 2

        row_nr, col_nr = row_base_nr - 1, col_base_nr
        matrix[row_nr][col_nr] = '(Capacity__________)'

        addr_category_names = []
        district_names = []

        row_nr, col_nr = row_base_nr, col_base_nr + 2
        col_capacity = col_nr

        matrix[row_nr][col_nr] = 'Person Care Capacity'

        row_nr, col_nr = row_base_nr + 2, col_base_nr
        row_first_district = row_nr
        col_district = col_nr

        for addr_category_name in addr_categories:

            addr_category_names.append(addr_category_name)
            addr_category = AddressCategory.search([
                ('name', '=', addr_category_name),
            ])

            person_sel_districts = PersonSelDistrict.search([
                ('addr_category_ids', '=', addr_category.id),
            ])
            for person_sel_district in person_sel_districts:
                district_names.append(person_sel_district.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_district.name
                row_last_district = row_nr
                row_nr += 1

            matrix[row_nr][col_nr] = addr_category.name
            row_last_district = row_nr
            row_nr += 1

            row_nr += 1

        row_total = row_nr

        matrix[row_total][col_base_nr] = 'Total'

        addr_category_capacity = 0
        total_capacity = 0
        for row_nr in range(row_first_district, row_last_district + 1):
            if (matrix[row_nr][col_district] is not False):
                district = matrix[row_nr][col_district].replace(mark_str, '')
                if district in district_names:
                    person_sel_district = PersonSelDistrict.search([
                        ('name', '=', district),
                    ])
                    matrix[row_nr][col_capacity] = format_number(person_sel_district.person_care_capacity)
                    addr_category_capacity = addr_category_capacity + person_sel_district.person_care_capacity
                if district in addr_category_names:
                    matrix[row_nr][col_capacity] = format_number(addr_category_capacity)
                    total_capacity = total_capacity + addr_category_capacity
                    addr_category_capacity = 0

        matrix[row_total][col_capacity] = format_number(total_capacity)

        # *********************************************************************************
        #
        # Planning
        #
        # *********************************************************************************

        row_base_nr = 1
        col_base_nr = col_capacity + 2

        # person_states = person_available_states

        row_nr, col_nr = row_base_nr - 1, col_base_nr
        matrix[row_nr][col_nr] = '(Planning________)'

        addr_category_names = []
        district_names = []
        person_category_names = []
        age_group_names = []

        row_nr, col_nr = row_base_nr, col_base_nr + 2
        row_age_group = row_nr
        col_first_age_group = col_nr

        for person_category_name in person_categories:

            person_category_names.append(person_category_name)
            person_category = PersonCategory.search([
                ('name', '=', person_category_name),
            ])

            person_sel_age_groups = PersonSelAgeGroup.search([
                ('person_category_ids', '=', person_category.id),
            ])
            for person_sel_age_group in person_sel_age_groups:
                age_group_names.append(person_sel_age_group.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_age_group.name
                col_last_age_group = col_nr
                col_nr += 1

            matrix[row_nr][col_nr] = person_category.name
            col_last_age_group = col_nr
            col_nr += 1

            col_nr += 1

        col_total = col_nr

        row_nr, col_nr = row_base_nr + 2, col_base_nr
        row_first_district = row_nr
        col_district = col_nr

        for addr_category_name in addr_categories:

            addr_category_names.append(addr_category_name)
            addr_category = AddressCategory.search([
                ('name', '=', addr_category_name),
            ])

            person_sel_districts = PersonSelDistrict.search([
                ('addr_category_ids', '=', addr_category.id),
            ])
            for person_sel_district in person_sel_districts:
                district_names.append(person_sel_district.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_district.name
                row_last_district = row_nr
                row_nr += 1

            matrix[row_nr][col_nr] = addr_category.name
            row_last_district = row_nr
            row_nr += 1

            row_nr += 1

        row_total = row_nr

        matrix[row_total][col_base_nr] = 'Total'
        matrix[row_base_nr][col_total] = 'Total'

        for row_nr in range(row_first_district, row_last_district + 1):
            for col_nr in range(col_first_age_group, col_last_age_group + 1):
                if (matrix[row_nr][col_district] is not False) and \
                   (matrix[row_age_group][col_nr] is not False):
                    district = matrix[row_nr][col_district].replace(mark_str, '')
                    age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                    if (district in district_names) and \
                       (age_group in age_group_names):

                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        person_sel_group = PersonSelGroup.search([
                            ('district_id', '=', person_sel_district.id),
                            ('age_group_id', '=', person_age_group.id),
                        ])

                        matrix[row_nr][col_nr] = format_number(person_sel_group.to_select_persons)

                    if (district in addr_category_names) and \
                       (age_group in age_group_names):

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        person_sel_groups = PersonSelGroup.search([
                            ('age_group_id', '=', person_age_group.id),
                        ])

                        count = 0
                        for person_sel_group in person_sel_groups:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            if (person_sel_group.district_id.addr_category_ids.id == addr_category_id):
                                count += person_sel_group.to_select_persons
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in district_names) and \
                       (age_group in person_category_names):

                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        person_sel_groups = PersonSelGroup.search([
                            ('district_id', '=', person_sel_district.id),
                        ])

                        count = 0
                        for person_sel_group in person_sel_groups:
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (person_sel_group.age_group_id.person_category_ids.id == person_category_id):
                                count += person_sel_group.to_select_persons
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in addr_category_names) and \
                       (age_group in person_category_names):

                        person_sel_groups = PersonSelGroup.search([])

                        count = 0
                        for person_sel_group in person_sel_groups:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (person_sel_group.age_group_id.person_category_ids.id == person_category_id) and \
                               (person_sel_group.district_id.addr_category_ids.id == addr_category_id):
                                count += person_sel_group.to_select_persons
                        matrix[row_nr][col_nr] = format_number(count)

        for row_nr in range(row_first_district, row_last_district + 1):
            if (matrix[row_nr][col_district] is not False):
                district = matrix[row_nr][col_district].replace(mark_str, '')
                if district in district_names:
                    person_sel_district = PersonSelDistrict.search([
                        ('name', '=', district),
                    ])
                    person_sel_groups = PersonSelGroup.search([
                        ('district_id', '=', person_sel_district.id),
                    ])
                    count = 0
                    for person_sel_group in person_sel_groups:
                        count += person_sel_group.to_select_persons
                    matrix[row_nr][col_total] = format_number(count)
                if district in addr_category_names:
                    addr_category_id = AddressCategory.search([
                        ('name', '=', district),
                    ]).id
                    person_sel_groups = PersonSelGroup.search([
                        ('district_id', '!=', False),
                    ])
                    count = 0
                    for person_sel_group in person_sel_groups:
                        if (person_sel_group.district_id.addr_category_ids.id == addr_category_id):
                            count += person_sel_group.to_select_persons
                        matrix[row_nr][col_total] = format_number(count)

        for col_nr in range(col_first_age_group, col_last_age_group + 1):
            if (matrix[row_age_group][col_nr] is not False):
                age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                if age_group in age_group_names:
                    person_sel_age_group = PersonSelAgeGroup.search([
                        ('name', '=', age_group),
                    ])
                    person_sel_groups = PersonSelGroup.search([
                        ('age_group_id', '=', person_sel_age_group.id),
                    ])
                    count = 0
                    for person_sel_group in person_sel_groups:
                        count += person_sel_group.to_select_persons
                    matrix[row_total][col_nr] = format_number(count)
                if age_group in person_category_names:
                    person_category_id = PersonCategory.search([
                        ('name', '=', age_group),
                    ]).id
                    person_sel_groups = PersonSelGroup.search([])
                    count = 0
                    for person_sel_group in person_sel_groups:
                        if (person_sel_group.age_group_id.person_category_ids.id == person_category_id):
                            count += person_sel_group.to_select_persons
                    matrix[row_total][col_nr] = format_number(count)

        person_sel_groups = PersonSelGroup.search([])

        count = 0
        for person_sel_group in person_sel_groups:
            count += person_sel_group.to_select_persons
        matrix[row_total][col_total] = format_number(count)

        # *********************************************************************************
        #
        # Selected
        #
        # *********************************************************************************

        row_base_nr = 1
        col_base_nr = col_total + 2

        person_states = person_selected_states

        row_nr, col_nr = row_base_nr - 1, col_base_nr
        matrix[row_nr][col_nr] = '(Selected________)'

        addr_category_names = []
        district_names = []
        person_category_names = []
        age_group_names = []

        row_nr, col_nr = row_base_nr, col_base_nr + 2
        row_age_group = row_nr
        col_first_age_group = col_nr

        for person_category_name in person_categories:

            person_category_names.append(person_category_name)
            person_category = PersonCategory.search([
                ('name', '=', person_category_name),
            ])

            person_sel_age_groups = PersonSelAgeGroup.search([
                ('person_category_ids', '=', person_category.id),
            ])
            for person_sel_age_group in person_sel_age_groups:
                age_group_names.append(person_sel_age_group.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_age_group.name
                col_last_age_group = col_nr
                col_nr += 1

            matrix[row_nr][col_nr] = person_category.name
            col_last_age_group = col_nr
            col_nr += 1

            col_nr += 1

        col_total = col_nr

        row_nr, col_nr = row_base_nr + 2, col_base_nr
        row_first_district = row_nr
        col_district = col_nr

        for addr_category_name in addr_categories:

            addr_category_names.append(addr_category_name)
            addr_category = AddressCategory.search([
                ('name', '=', addr_category_name),
            ])

            person_sel_districts = PersonSelDistrict.search([
                ('addr_category_ids', '=', addr_category.id),
            ])
            for person_sel_district in person_sel_districts:
                district_names.append(person_sel_district.name)
                matrix[row_nr][col_nr] = mark_str + person_sel_district.name
                row_last_district = row_nr
                row_nr += 1

            matrix[row_nr][col_nr] = addr_category.name
            row_last_district = row_nr
            row_nr += 1

            row_nr += 1

        row_total = row_nr

        matrix[row_total][col_base_nr] = 'Total'
        matrix[row_base_nr][col_total] = 'Total'

        for row_nr in range(row_first_district, row_last_district + 1):
            for col_nr in range(col_first_age_group, col_last_age_group + 1):
                if (matrix[row_nr][col_district] is not False) and \
                   (matrix[row_age_group][col_nr] is not False):
                    district = matrix[row_nr][col_district].replace(mark_str, '')
                    age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                    if (district in district_names) and \
                       (age_group in age_group_names):

                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                            ('age_reference_years', '>=', person_age_group.min_age),
                            ('age_reference_years', '<=', person_age_group.max_age),
                        ])

                        count = 0
                        for available_person in available_persons:
                            person_category_id = PersonCategory.search([
                                ('name', '=', person_age_group.person_category_ids.name),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.district == person_sel_district.name):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in addr_category_names) and \
                       (age_group in age_group_names):

                        person_age_group = PersonSelAgeGroup.search([
                            ('name', '=', age_group),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                            ('age_reference_years', '>=', person_age_group.min_age),
                            ('age_reference_years', '<=', person_age_group.max_age),
                        ])

                        count = 0
                        for available_person in available_persons:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            person_category_id = PersonCategory.search([
                                ('name', '=', person_age_group.person_category_ids.name),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.category_ids.id == addr_category_id):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in district_names) and \
                       (age_group in person_category_names):

                        person_sel_district = PersonSelDistrict.search([
                            ('name', '=', district),
                        ])

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                        ])

                        count = 0
                        for available_person in available_persons:
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.district == person_sel_district.name):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

                    if (district in addr_category_names) and \
                       (age_group in person_category_names):

                        available_persons = Person.search([
                            ('state', 'in', person_states),
                            ('phase_id', '=', self.phase_id.id),
                        ])

                        count = 0
                        for available_person in available_persons:
                            addr_category_id = AddressCategory.search([
                                ('name', '=', district),
                            ]).id
                            person_category_id = PersonCategory.search([
                                ('name', '=', age_group),
                            ]).id
                            if (available_person.category_ids.id == person_category_id) and \
                               (available_person.ref_address_id.category_ids.id == addr_category_id):
                                count += 1
                        matrix[row_nr][col_nr] = format_number(count)

        for row_nr in range(row_first_district, row_last_district + 1):
            if (matrix[row_nr][col_district] is not False):
                district = matrix[row_nr][col_district].replace(mark_str, '')
                if district in district_names:
                    person_sel_district = PersonSelDistrict.search([
                        ('name', '=', district),
                    ])
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])
                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id is not False) and \
                           (available_person.ref_address_id.district == person_sel_district.name):
                            count += 1
                    matrix[row_nr][col_total] = format_number(count)
                if district in addr_category_names:
                    addr_category_id = AddressCategory.search([
                        ('name', '=', district),
                    ]).id
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])
                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id is not False) and \
                           (available_person.ref_address_id.category_ids.id == addr_category_id):
                            count += 1
                    matrix[row_nr][col_total] = format_number(count)

        for col_nr in range(col_first_age_group, col_last_age_group + 1):
            if (matrix[row_age_group][col_nr] is not False):
                age_group = matrix[row_age_group][col_nr].replace(mark_str, '')
                if age_group in age_group_names:
                    person_sel_age_group = PersonSelAgeGroup.search([
                        ('name', '=', age_group),
                    ])
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                        ('age_reference_years', '>=', person_sel_age_group.min_age),
                        ('age_reference_years', '<=', person_sel_age_group.max_age),
                    ])
                    person_category_id = PersonCategory.search([
                        ('name', '=', person_sel_age_group.person_category_ids.name),
                    ]).id
                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id == person_category_id) and \
                           (available_person.ref_address_id.category_ids.id is not False):
                            count += 1
                    matrix[row_total][col_nr] = format_number(count)
                if age_group in person_category_names:
                    person_category_id = PersonCategory.search([
                        ('name', '=', age_group),
                    ]).id
                    available_persons = Person.search([
                        ('state', 'in', person_states),
                        ('phase_id', '=', self.phase_id.id),
                    ])
                    count = 0
                    for available_person in available_persons:
                        if (available_person.category_ids.id == person_category_id) and \
                           (available_person.ref_address_id.category_ids.id is not False):
                            count += 1
                    matrix[row_total][col_nr] = format_number(count)

        count = 0
        for available_person in available_persons:
            if (available_person.category_ids.id is not False) and \
               (available_person.ref_address_id.category_ids.id is not False):
                count += 1
        matrix[row_total][col_total] = format_number(count)

        # *********************************************************************************
        #
        # Table Processing
        #
        # *********************************************************************************

        PersonSelSummary = self.env['clv.person_sel.summary']
        person_sel_summary = PersonSelSummary.search([])
        person_sel_summary.unlink()

        rows = []
        for row_nr in range(0, row_max + 1):
            name = str(row_nr)
            while len(name) < 3:
                name = '0' + name
            name = 'r' + name
            values = {
                'name': name,
            }
            rows.append(PersonSelSummary.create(values))

        for row_nr in range(0, row_max + 1):
            for col_nr in range(1, col_max + 1):
                col_str = str(col_nr)
                while len(col_str) < 3:
                    col_str = '0' + col_str
                col_str = 'c' + col_str
                command = 'rows[{}].{} = matrix[{}][{}]'.format(row_nr, col_str, row_nr, col_nr)
                exec(command)

        _logger.info(u'%s %s %s %s',
                     '>>>>>', 'do_person_sel_summary_setup', ' - Execution time:', secondsToStr(time() - start)
                     )

        return True
