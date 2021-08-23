# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PersonSelSummary(models.AbstractModel):
    _description = 'Abstract Row'
    _name = 'clv.abstract.row'
    _order = 'name'

    name = fields.Char(string='Row', required=True)

    c001 = fields.Char(string='C001', required=False)
    c002 = fields.Char(string='C002', required=False)
    c003 = fields.Char(string='C003', required=False)
    c004 = fields.Char(string='C004', required=False)
    c005 = fields.Char(string='C005', required=False)
    c006 = fields.Char(string='C006', required=False)
    c007 = fields.Char(string='C007', required=False)
    c008 = fields.Char(string='C008', required=False)
    c009 = fields.Char(string='C009', required=False)
    c010 = fields.Char(string='C010', required=False)
    c011 = fields.Char(string='C011', required=False)
    c012 = fields.Char(string='C012', required=False)
    c013 = fields.Char(string='C013', required=False)
    c014 = fields.Char(string='C014', required=False)
    c015 = fields.Char(string='C015', required=False)
    c016 = fields.Char(string='C016', required=False)
    c017 = fields.Char(string='C017', required=False)
    c018 = fields.Char(string='C018', required=False)
    c019 = fields.Char(string='C019', required=False)
    c020 = fields.Char(string='C020', required=False)
    c021 = fields.Char(string='C021', required=False)
    c022 = fields.Char(string='C022', required=False)
    c023 = fields.Char(string='C023', required=False)
    c024 = fields.Char(string='C024', required=False)
    c025 = fields.Char(string='C025', required=False)
    c026 = fields.Char(string='C026', required=False)
    c027 = fields.Char(string='C027', required=False)
    c028 = fields.Char(string='C028', required=False)
    c029 = fields.Char(string='C029', required=False)
    c030 = fields.Char(string='C030', required=False)
    c031 = fields.Char(string='C031', required=False)
    c032 = fields.Char(string='C032', required=False)
    c033 = fields.Char(string='C033', required=False)
    c034 = fields.Char(string='C034', required=False)
    c035 = fields.Char(string='C035', required=False)
    c036 = fields.Char(string='C036', required=False)
    c037 = fields.Char(string='C037', required=False)
    c038 = fields.Char(string='C038', required=False)
    c039 = fields.Char(string='C039', required=False)
    c040 = fields.Char(string='C040', required=False)
    c041 = fields.Char(string='C041', required=False)
    c042 = fields.Char(string='C042', required=False)
    c043 = fields.Char(string='C043', required=False)
    c044 = fields.Char(string='C044', required=False)
    c045 = fields.Char(string='C045', required=False)
    c046 = fields.Char(string='C046', required=False)
    c047 = fields.Char(string='C047', required=False)
    c048 = fields.Char(string='C048', required=False)
    c049 = fields.Char(string='C049', required=False)
    c050 = fields.Char(string='C050', required=False)
    c051 = fields.Char(string='C051', required=False)
    c052 = fields.Char(string='C052', required=False)
    c053 = fields.Char(string='C053', required=False)
    c054 = fields.Char(string='C054', required=False)
    c055 = fields.Char(string='C055', required=False)
    c056 = fields.Char(string='C056', required=False)
    c057 = fields.Char(string='C057', required=False)
    c058 = fields.Char(string='C058', required=False)
    c059 = fields.Char(string='C059', required=False)
    c060 = fields.Char(string='C060', required=False)
    c061 = fields.Char(string='C061', required=False)
    c062 = fields.Char(string='C062', required=False)
    c063 = fields.Char(string='C063', required=False)
    c064 = fields.Char(string='C064', required=False)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE(name)',
         u'Error! The Row must be unique!'
         ),
    ]
