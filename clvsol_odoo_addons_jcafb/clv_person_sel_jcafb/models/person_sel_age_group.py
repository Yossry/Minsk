# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PersonSelAgeGroup(models.Model):
    _description = 'Person Selection Age-Group'
    _name = 'clv.person_sel.age_group'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Code', required=False)

    min_age = fields.Char(string='Minimum Age', required=False)
    max_age = fields.Char(string='Maximum Age', required=False)

    available_persons = fields.Integer(string='Available Persons', required=False)
    selected_persons = fields.Integer(string='Selected Persons', required=False)

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE(name)',
         u'Error! The Name must be unique!'
         ),
        ('code_uniq',
         'UNIQUE(code)',
         u'Error! The Code must be unique!'
         ),
    ]


class PersonSelAgeGroup_2(models.Model):
    _inherit = 'clv.person_sel.age_group'

    person_category_ids = fields.Many2many(
        comodel_name='clv.person.category',
        relation='clv_person_sel_age_group_person_category_rel',
        column1='age_group_id',
        column2='person_category_id',
        string='Person Categories'
    )
    person_category_names = fields.Char(
        string='Person Category Names',
        compute='_compute_person_category_names',
        store=True
    )
    person_category_names_suport = fields.Char(
        string='Person Category Names Suport',
        compute='_compute_person_category_names_suport',
        store=False
    )

    @api.depends('person_category_ids')
    def _compute_person_category_names(self):
        for r in self:
            r.person_category_names = r.person_category_names_suport

    @api.multi
    def _compute_person_category_names_suport(self):
        for r in self:
            person_category_names = False
            for person_category in r.person_category_ids:
                if person_category_names is False:
                    person_category_names = person_category.complete_name
                else:
                    person_category_names = person_category_names + ', ' + person_category.complete_name
            r.person_category_names_suport = person_category_names
            if r.person_category_names != person_category_names:
                record = self.env['clv.person_sel.age_group'].search([('id', '=', r.id)])
                record.write({'person_category_ids': r.person_category_ids})
