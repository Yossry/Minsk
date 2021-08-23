# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ProcessingScheduleExecute(models.TransientModel):
    _description = 'Processing Schedule Execute'
    _name = 'clv.processing.schedule.execute'

    def _default_processing_schedule_ids(self):
        return self._context.get('active_ids')
    processing_schedule_ids = fields.Many2many(
        comodel_name='clv.processing.schedule',
        relation='clv_processing_schedule_execute_rel',
        string='Processing Schedules',
        default=_default_processing_schedule_ids)

    @api.multi
    def do_processing_schedule_execute(self):
        self.ensure_one()

        for processing_schedule in self.processing_schedule_ids:

            _logger.info(u'%s %s', '>>>>>', processing_schedule.name)

            model = False
            if processing_schedule.model is not False:
                model = processing_schedule.model

            method = False
            if processing_schedule.method is not False:
                method = processing_schedule.method

            method_call = False

            if (model is not False) and (method is not False):

                method_call = 'self.env["' + model + '"].' + method + '(processing_schedule)'

            _logger.info(u'%s %s', '>>>>>>>>>> method_call:', method_call)

            exec(method_call)

        return True
