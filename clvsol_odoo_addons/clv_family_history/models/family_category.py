# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class FamilyCategory(models.Model):
    _inherit = 'clv.family.category'

    family_history_ids = fields.Many2many(
        comodel_name='clv.family.history',
        relation='clv_family_history_category_rel',
        column1='category_id',
        column2='family_history_id',
        string='Families (History)'
    )


class FamilyHistory(models.Model):
    _inherit = "clv.family.history"

    category_ids = fields.Many2many(
        comodel_name='clv.family.category',
        relation='clv_family_history_category_rel',
        column1='family_history_id',
        column2='category_id',
        string='Categories'
    )
    category_names = fields.Char(
        string='Category Names',
        compute='_compute_category_names',
        store=True
    )
    category_names_suport = fields.Char(
        string='Category Names Suport',
        compute='_compute_category_names_suport',
        store=False
    )

    @api.depends('category_ids')
    def _compute_category_names(self):
        for r in self:
            r.category_names = r.category_names_suport

    @api.multi
    def _compute_category_names_suport(self):
        for r in self:
            category_names = False
            for category in r.category_ids:
                if category_names is False:
                    category_names = category.complete_name
                else:
                    category_names = category_names + ', ' + category.complete_name
            r.category_names_suport = category_names
            if r.category_names != category_names:
                record = self.env['clv.family'].search([('id', '=', r.id)])
                record.write({'category_ids': r.category_ids})
