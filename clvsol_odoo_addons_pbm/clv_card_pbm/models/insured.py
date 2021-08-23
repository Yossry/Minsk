# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, fields, models


class Insured(models.Model):
    _inherit = 'clv.insured'

    card_ids = fields.One2many(
        comodel_name='clv.card',
        inverse_name='insured_id',
        string='Cards'
    )
    count_cards = fields.Integer(
        string='Number of Cards',
        compute='_compute_count_cards',
        store=True
    )

    @api.depends('card_ids')
    def _compute_count_cards(self):
        for r in self:
            r.count_cards = len(r.card_ids)


class Card(models.Model):
    _inherit = "clv.card"

    insured_id = fields.Many2one(
        comodel_name='clv.insured',
        string='Insured',
        ondelete='restrict'
    )
    insured_name = fields.Char(
        string='Insured Name',
        related='insured_id.name',
        store=False,
        readonly=True
    )
    insured_code = fields.Char(
        string='Insured Code',
        related='insured_id.code',
        store=False,
        readonly=True
    )
    insured_alias = fields.Char(
        string='Insured Alias',
        related='insured_id.alias',
        store=False,
        readonly=True
    )
    insured_main_insured_id = fields.Many2one(
        comodel_name='clv.insured',
        string='Main Insured',
        related='insured_id.main_insured_id',
        store=True,
        readonly=True
    )
    insured_birthday = fields.Date(
        string="Insured Date of Birth",
        related='insured_id.birthday',
        store=False,
        readonly=True
    )
    insured_gender = fields.Selection(
        [('M', 'Male'),
         ('F', 'Female'),
         ('O', 'Other'),
         ],
        string='Insured Gender',
        related='insured_id.gender',
        store=True,
        readonly=True
    )
    insured_insured_group_id = fields.Many2one(
        comodel_name='clv.insured_group',
        string='Insured Group',
        related='insured_id.insured_group_id',
        store=True,
        readonly=True
    )
    insured_group_reg_number = fields.Char(
        string='Register Number',
        help='Insured Register Number at Insured Group.',
        related='insured_id.group_reg_number',
        store=False,
        readonly=True
    )
    insured_insurance_plan_id = fields.Many2one(
        comodel_name='clv.insurance_plan',
        string='Insurance Plan',
        related='insured_id.insurance_plan_id',
        store=True,
        readonly=True
    )
    insured_state = fields.Selection(
        [('draft', 'New'),
         ('processing', 'Processing'),
         ('active', 'Active'),
         ('suspended', 'Suspended'),
         ('cancelled', 'Cancelled'),
         ],
        string='Insured State',
        related='insured_id.state',
        store=True,
        readonly=True
    )
    insured_category_names = fields.Char(
        string='Insured Categories',
        related='insured_id.category_names',
        store=True,
        readonly=True
    )
    insured_date_inclusion = fields.Datetime(
        string="Insured Inclusion Date",
        related='insured_id.date_inclusion',
        store=False,
        readonly=True
    )
