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


class ModelExport(models.Model):
    _name = 'clv.model_export'
    _inherit = 'clv.model_export'

    model_export_card_ids = fields.Many2many(
        comodel_name='clv.card',
        relation='clv_model_export_card_rel',
        column1='card_id',
        column2='model_export_id',
        string='Data Export Cards'
    )
    count_model_export_cards = fields.Integer(
        string='Cards',
        compute='_compute_count_model_export_cards',
        store=True
    )

    @api.depends('model_export_card_ids')
    def _compute_count_model_export_cards(self):
        for r in self:
            r.count_model_export_cards = len(r.model_export_card_ids)

    @api.depends('model_model')
    def compute_model_items(self):
        for r in self:
            if r.model_model == 'clv.card':
                r.model_items = 'model_export_card_ids'
        super(ModelExport, self).compute_model_items()
