# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from functools import reduce

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ModelExport(models.Model):
    _inherit = 'clv.model_export'

    export_person_ids = fields.Many2many(
        comodel_name='clv.person',
        relation='clv_export_person_rel',
        column1='person_id',
        column2='export_id',
        string='Export Persons'
    )
    count_export_persons = fields.Integer(
        string='Persons (count)',
        compute='_compute_count_export_persons',
        store=True
    )

    @api.depends('export_person_ids')
    def _compute_count_export_persons(self):
        for r in self:
            r.count_export_persons = len(r.export_person_ids)

    @api.depends('model_model')
    def compute_model_items(self):
        for r in self:
            if self.model_model == 'clv.person':
                r.model_items = 'export_person_ids'
        super().compute_model_items()


class ModelExport_xls(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_xls_person(self):

        self.do_model_export_execute_xls()


class ModelExport_csv(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_csv_person(self):

        self.do_model_export_execute_csv()


class ModelExport_sqlite(models.Model):
    _inherit = 'clv.model_export'

    @api.multi
    def do_model_export_execute_sqlite_person(self):

        self.do_model_export_execute_sqlite()
