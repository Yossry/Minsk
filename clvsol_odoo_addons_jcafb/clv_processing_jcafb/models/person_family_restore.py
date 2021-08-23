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

    def _do_person_family_restore(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> schedule:', schedule.name)

        phase_name = 'JCAFB-2019'
        Phase = self.env['clv.phase']
        phase = Phase.search([
            ('name', '=', phase_name),
        ])

        PersonHistory = self.env['clv.person.history']
        person_histories = PersonHistory.search([
            ('phase_id', '=', phase.id),
        ])

        Person = self.env['clv.person']

        for person_history in person_histories:

            _logger.info(u'%s %s', '>>>>>>>>>>>>>>>>>>>> person:', person_history.person_id.name)
            _logger.info(u'%s %s', '>>>>>>>>>>>>>>>>>>>> family:', person_history.ref_family_id.name)

            if person_history.person_id.family_id.id != person_history.ref_family_id.id:

                _logger.warning(u'%s %s', '>>>>>>>>>>>>>>>>>>>> family:', 'Family Mismatch')

                person = Person.search([
                    ('id', '=', person_history.person_id.id),
                ])

                values = {}
                values['family_id'] = person_history.ref_family_id.id
                values['reg_state'] = 'revised'
                _logger.warning(u'%s %s', '>>>>>>>>>>>>>>>>>>>> values:', values)
                person.write(values)
