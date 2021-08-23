# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from functools import reduce

from odoo import models, fields

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractReport(models.AbstractModel):
    _description = 'Abstract Report'
    _name = 'clv.abstract.report'

    date_report = fields.Datetime(string="Report Date")
    report_status = fields.Selection(
        [('draft', 'Draft'),
         ('revised', 'Revised'),
         ('done', 'Done'),
         ('canceled', 'Canceled'),
         ], string='Report Status', default='draft'
    )
    report_outcomes = fields.Text(string='Report Outcomes')

    def _object_report(self, schedule, model_name):

        from time import time
        start = time()

        _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))

        schedule.report_log +=  \
            'Execution time: ' + str(secondsToStr(time() - start)) + '\n'
