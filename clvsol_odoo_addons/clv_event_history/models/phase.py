# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class Phase(models.Model):
    _inherit = 'clv.phase'

    event_ids = fields.One2many(
        comodel_name='clv.event',
        inverse_name='phase_id',
        string='Events',
        readonly=True
    )
    count_events = fields.Integer(
        string='Events (count)',
        compute='_compute_event_ids_and_count',
    )

    @api.multi
    def _compute_event_ids_and_count(self):
        for record in self:

            search_domain = [
                ('phase_id', '=', record.id),
            ]

            events = self.env['clv.event'].search(search_domain)

            record.count_events = len(events)
            record.event_ids = [(6, 0, events.ids)]


class Event(models.Model):
    _inherit = 'clv.event'

    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        ondelete='restrict'
    )


class EventAttendee(models.Model):
    _inherit = 'clv.event.attendee'

    event_phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Event Phase',
        related='event_id.phase_id',
        store=True
    )
