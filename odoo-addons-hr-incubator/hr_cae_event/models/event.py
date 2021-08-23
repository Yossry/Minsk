# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import html_translate


class EventType(models.Model):
    _inherit = "event.type"

    description = fields.Html(
        string="Description",
        oldname="note",
        translate=html_translate,
        sanitize_attributes=False,
        readonly=False,
    )


class Event(models.Model):
    _inherit = "event.event"

    department_id = fields.Many2one("hr.department", string="Department")
    duration = fields.Float(
        string="Duration", compute="_compute_duration", help="hours"
    )

    @api.depends("date_begin", "date_end")
    @api.multi
    def _compute_duration(self):
        for event in self:
            if event.date_begin and event.date_end:
                duration = (
                    event.date_end - event.date_begin
                ).total_seconds() / 3600
            else:
                duration = False
            event.duration = duration

    @api.onchange("event_type_id")
    def _onchange_type(self):
        res = super()._onchange_type()

        if self.event_type_id.description:
            self.description = self.event_type_id.description

        return res
