# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ModelExportExecute(models.TransientModel):
    _description = 'Model Export Execute'
    _name = 'clv.model_export.execute'

    def _default_model_export_ids(self):
        return self._context.get('active_ids')
    model_export_ids = fields.Many2many(
        comodel_name='clv.model_export',
        relation='clv_model_export_execute_rel',
        string='Model Exports',
        default=_default_model_export_ids)

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_model_export_execute(self):
        self.ensure_one()

        ModelExportMethod = self.env['clv.model_export.method']

        for model_export in self.model_export_ids:

            _logger.info(u'%s %s', '>>>>>', model_export.name)

            model = model_export.model_model
            export_type = model_export.export_type

            model_export_method = ModelExportMethod.search([
                ('name', '=', model),
                ('export_type', '=', export_type),
            ])
            method = False
            if model_export_method.id is not False:
                method = model_export_method.method

            method_call = False

            if method is not False:

                method_call = 'model_export.' + method + '()'

            else:

                if export_type == 'xls':
                    method_call = 'model_export.do_model_export_execute_xls()'

                if export_type == 'csv':
                    method_call = 'model_export.do_model_export_execute_csv()'

                if export_type == 'sqlite':
                    method_call = 'model_export.do_model_export_execute_sqlite()'

            _logger.info(u'%s %s', '>>>>>>>>>> method_call:', method_call)

            exec(method_call)

        return True
