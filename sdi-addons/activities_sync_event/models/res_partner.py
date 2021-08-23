# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools, _


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def schedule_meeting(self):
        """
        Add partner's name to action's context to put in the summary and add
        the partner to the attendees of the meeting.
        :return:
        """
        self.ensure_one()
        action = super(Partner, self).schedule_meeting()
        name = self.name
        if not self.is_company:
            if self.commercial_company_name:
                name = "{}, {}".format(self.commercial_company_name,
                                       self.name)
            elif not self.commercial_company_name and self.parent_id.name:
                name = "{}, {}".format(self.parent_id.name,
                                       self.name)
            else:
                name = self.name

        action['context']['default_name'] = name
        action['context']['default_res_id'] = self.id
        action['context']['default_res_model'] = 'res.partner'
        action['context']['search_default_partner_ids'] = ""
        action['context']['default_partner_ids'] = self.env.user.partner_id.ids
        return action
