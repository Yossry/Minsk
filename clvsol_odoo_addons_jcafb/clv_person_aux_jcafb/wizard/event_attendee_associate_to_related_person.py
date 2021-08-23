# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventAttendeeAssociateToRelatedPerson(models.TransientModel):
    _description = 'Event Attendee  Associate to Related Person'
    _name = 'clv.event.attendee.associate_to_related_person'

    def _default_event_attendee_ids(self):
        return self._context.get('active_ids')
    event_attendee_ids = fields.Many2many(
        comodel_name='clv.event.attendee',
        relation='clv_event_attendee_associate_to_related_person_rel',
        string='Event Attendee s',
        default=_default_event_attendee_ids
    )

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
    def do_event_attendee_associate_to_related_person(self):
        self.ensure_one()

        event_attendee_count = 0
        for event_attendee in self.event_attendee_ids:

            event_attendee_count += 1

            _logger.info(u'%s %s %s', '>>>>>', event_attendee_count, event_attendee.display_name)

            if event_attendee.ref_id.related_person_id.id is not False:

                related_person = event_attendee.ref_id.related_person_id
                ref_id = related_person._name + ',' + str(related_person.id)
                event_attendee.ref_id = ref_id

                _logger.info(u'%s %s', '>>>>>>>>>>', event_attendee.ref_id.name)

        return True
