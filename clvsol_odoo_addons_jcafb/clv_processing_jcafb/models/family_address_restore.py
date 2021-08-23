# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from functools import reduce

from odoo import models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractProcess(models.AbstractModel):
    _inherit = 'clv.abstract.process'

    def _do_family_address_restore(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> schedule:', schedule.name)

        phase_name = 'JCAFB-2019'
        Phase = self.env['clv.phase']
        phase = Phase.search([
            ('name', '=', phase_name),
        ])

        FamilyHistory = self.env['clv.family.history']
        family_histories = FamilyHistory.search([
            ('phase_id', '=', phase.id),
        ])

        Family = self.env['clv.family']

        for family_history in family_histories:

            _logger.info(u'%s %s', '>>>>>>>>>>>>>>>>>>>> family:', family_history.family_id.name)
            _logger.info(u'%s %s', '>>>>>>>>>>>>>>>>>>>> address:', family_history.ref_address_id.name)

            if family_history.family_id.ref_address_id.id != family_history.ref_address_id.id:

                _logger.warning(u'%s %s', '>>>>>>>>>>>>>>>>>>>> address:', 'Address Mismatch')

                family = Family.search([
                    ('id', '=', family_history.family_id.id),
                ])

                values = {}
                values['ref_address_id'] = family_history.ref_address_id.id
                values['reg_state'] = 'revised'
                _logger.warning(u'%s %s', '>>>>>>>>>>>>>>>>>>>> values:', values)
                family.write(values)
