# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PersonSelDistrict(models.Model):
    _description = 'Person Selection District'
    _name = 'clv.person_sel.district'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Code', required=False)

    person_care_capacity = fields.Integer(string='Person Care Capacity', required=False)
    address_care_capacity = fields.Integer(string='Address Care Capacity', required=False)

    # address_nr = fields.Integer(string='Number of Addresses', required=False)

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


class PersonSelDistrict_2(models.Model):
    _inherit = "clv.person_sel.district"

    addr_category_ids = fields.Many2many(
        comodel_name='clv.address.category',
        relation='clv_person_sel_district_addr_category_rel',
        column1='person_sel_district_id',
        column2='addr_category_id',
        string='Address Categories'
    )
    addr_category_names = fields.Char(
        string='Address Category Names',
        compute='_compute_addr_category_names',
        store=True
    )
    addr_category_names_suport = fields.Char(
        string='Address Category Names Suport',
        compute='_compute_addr_category_names_suport',
        store=False
    )

    @api.depends('addr_category_ids')
    def _compute_addr_category_names(self):
        for r in self:
            r.addr_category_names = r.addr_category_names_suport

    @api.multi
    def _compute_addr_category_names_suport(self):
        for r in self:
            addr_category_names = False
            for addr_category in r.addr_category_ids:
                if addr_category_names is False:
                    addr_category_names = addr_category.complete_name
                else:
                    addr_category_names = addr_category_names + ', ' + addr_category.complete_name
            r.addr_category_names_suport = addr_category_names
            if r.addr_category_names != addr_category_names:
                record = self.env['clv.person_sel.district'].search([('id', '=', r.id)])
                record.write({'addr_category_ids': r.addr_category_ids})

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
                record = self.env['clv.address'].search([('id', '=', r.id)])
                record.write({'category_ids': r.category_ids})
