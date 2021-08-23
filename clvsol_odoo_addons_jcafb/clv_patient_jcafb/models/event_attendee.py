# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = 'clv.patient'

    event_attendee_ids = fields.One2many(
        string='Event Attendees',
        comodel_name='clv.event.attendee',
        compute='_compute_event_attendee_ids_and_count',
    )
    count_events = fields.Integer(
        string='Events',
        compute='_compute_event_attendee_ids_and_count',
    )

    @api.multi
    def _compute_event_attendee_ids_and_count(self):
        for record in self:
            event_attendees = self.env['clv.event.attendee'].search([
                ('ref_id', '=', self._name + ',' + str(record.id)),
            ])
            record.count_events = len(event_attendees)
            record.event_attendee_ids = [(6, 0, event_attendees.ids)]
