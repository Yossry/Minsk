# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AddressMarker(models.Model):
    _inherit = 'clv.address.marker'

    address_history_ids = fields.Many2many(
        comodel_name='clv.address.history',
        relation='clv_address_history_marker_rel',
        column1='marker_id',
        column2='address_history_id',
        string='Addresses (History)'
    )


class AddressHistory(models.Model):
    _inherit = "clv.address.history"

    marker_ids = fields.Many2many(
        comodel_name='clv.address.marker',
        relation='clv_address_history_marker_rel',
        column1='address_history_id',
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
