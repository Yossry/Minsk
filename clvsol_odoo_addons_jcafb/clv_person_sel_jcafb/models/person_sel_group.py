# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo import api, fields, models
from odoo import fields, models


class PersonSelGroup(models.Model):
    _description = 'Person Selection Group'
    _name = 'clv.person_sel.group'
    _order = 'name'

    name = fields.Char(string='Name', required=False)

    code = fields.Char(string='Code', required=False)

    available_persons = fields.Integer(string='Available Persons', required=False)
    to_select_persons = fields.Integer(string='To Select Persons', required=False)
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


class PersonSelGroup_4(models.Model):
    _inherit = "clv.person_sel.group"

    district_id = fields.Many2one(
        comodel_name='clv.person_sel.district',
        string='District',
        ondelete='restrict'
    )
    addr_category_names = fields.Char(
        string='Address Category Names',
        related='district_id.addr_category_names',
        store=True
    )

    age_group_id = fields.Many2one(
        comodel_name='clv.person_sel.age_group',
        string='Age-Group',
        ondelete='restrict'
    )
    person_category_names = fields.Char(
        string='Person Category Names',
        related='age_group_id.person_category_names',
        store=True
    )
