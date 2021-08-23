# Copyright 2018 David Juaneda - <djuaneda@sdi.es>
# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, fields, models

_unlink = logging.getLogger(__name__ + '.unlink')


class Meeting(models.Model):
    _inherit = 'calendar.event'

    editable = fields.Boolean(compute='_compute_event_is_editable')

    @api.multi
    @api.onchange('active')
    def _compute_event_is_editable(self):
        """ Check if activity is editable and set the attibute of instance."""
        for event in self:
            activity = self.env['mail.activity'].search([('calendar_event_id', '=', event.id)])
            event.editable = True if activity.active else False

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Modify method from class 'BaseModel' for to include 'editable' field.

        :param domain: Search domain, see ``args`` parameter in ``search()``. Defaults to an empty domain that will match all records.
        :param fields: List of fields to read, see ``fields`` parameter in ``read()``. Defaults to all fields.
        :param offset: Number of records to skip, see ``offset`` parameter in ``search()``. Defaults to 0.
        :param limit: Maximum number of records to return, see ``limit`` parameter in ``search()``. Defaults to no limit.
        :param order: Columns to sort result, see ``order`` parameter in ``search()``. Defaults to no sort.
        :return: List of dictionaries containing the asked fields.
        :rtype: List of dictionaries.
        """
        if not fields:
            fields=[]
        fields.append('editable')

        return  super(Meeting,self).search_read(domain, fields, offset, limit, order)

    @api.multi
    def unlink(self, can_be_deleted=True):
        """
        Override.
        Modification of the method so that it also eliminates the activity in the wall.
        :param can_be_deleted:
        :return:
        """
        for event in self:
            id = event.user_id.partner_id.id
            result = super(Meeting,self).unlink(can_be_deleted)
            if result:
                self.invalidate_cache()
                self.recompute()
                self.env['bus.bus'].sendone(
                    (self._cr.dbname, 'res.partner', id),
                    {'type': 'activity_updated', 'activity_deleted': True})
        return result
