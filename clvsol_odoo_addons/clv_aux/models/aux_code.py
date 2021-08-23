# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AuxiliaryCode(models.Model):
    _description = 'Auxiliary Code'
    _name = 'clv.aux.code'
    _inherit = 'clv.abstract.code'
    _rec_name = 'code'
    _order = 'code'

    code = fields.Char(string='Auxiliary Code', required=True, default='/')
    code_sequence = fields.Char(string='Code Sequence', required=True, default=False)

    aux_instance_id = fields.Many2one(
        comodel_name='clv.aux.instance',
        string='Auxiliary Instance',
        ondelete='restrict'
    )

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
