# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import api, fields, models


def get_random_field():

    random_field = str(random.randrange(1, 2147483647))
    while len(random_field) < 10:
        random_field = '0' + random_field

    return random_field


class AbstractRandom(models.AbstractModel):
    _description = 'Abstract Random'
    _name = 'clv.abstract.random'
    _order = 'random_field'

    random_field = fields.Char(
        string='Random ID', index=True, required=False, default='/',
        help='Use "/" to get an automatic new Random ID.'
    )

    @api.model
    def create(self, values):
        if 'random_field' not in values or ('random_field' in values and values['random_field'] == '/'):
            random_field = get_random_field()
            values['random_field'] = random_field
        return super().create(values)

    @api.multi
    def write(self, values):
        if 'random_field' in values and values['random_field'] == '/':
            random_field = get_random_field()
            values['random_field'] = random_field
        return super().write(values)

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'random_field': '/', })
        return super().copy(default)
