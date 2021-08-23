# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PersonMarker(models.Model):
    _description = 'Person Marker'
    _name = 'clv.person.marker'
    _inherit = 'clv.abstract.marker'

    code = fields.Char(string='Marker Code', required=False)

    person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='clv_person_marker_rel',
        column1='marker_id',
        column2='person_id',
        string='Persons'
    )


class Person(models.Model):
    _inherit = "clv.person"

    marker_ids = fields.Many2many(
        comodel_name='clv.person.marker',
        relation='clv_person_marker_rel',
        column1='person_id',
        column2='marker_id',
        string='Markers'
    )
    marker_names = fields.Char(
        string='Marker Names',
        compute='_compute_marker_names',
        store=True
    )

    @api.depends('marker_ids')
    def _compute_marker_names(self):
        for r in self:
            marker_names = False
            for marker in r.marker_ids:
                if marker_names is False:
                    marker_names = marker.name
                else:
                    marker_names = marker_names + ', ' + marker.name
            r.marker_names = marker_names
