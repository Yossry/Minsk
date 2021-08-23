# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SetCategory(models.Model):
    _description = 'Set Category'
    _name = 'clv.set.category'
    _inherit = 'clv.abstract.category'

    code = fields.Char(string='Category Code', required=False)

    parent_id = fields.Many2one(
        comodel_name='clv.set.category',
        string='Parent Category',
        index=True,
        ondelete='restrict'
    )

    child_ids = fields.One2many(
        comodel_name='clv.set.category',
        inverse_name='parent_id',
        string='Child Categories'
    )

    set_ids = fields.Many2many(
        comodel_name='clv.set',
        relation='clv_set_category_rel',
        column1='category_id',
        column2='set_id',
        string='Sets'
    )

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]


class Set(models.Model):
    _inherit = "clv.set"

    category_ids = fields.Many2many(
        comodel_name='clv.set.category',
        relation='clv_set_category_rel',
        column1='set_id',
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
                record = self.env['clv.set'].search([('id', '=', r.id)])
                record.write({'category_ids': r.category_ids})
