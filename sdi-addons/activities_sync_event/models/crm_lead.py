# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def _compute_meeting_count(self):
        super(Lead,self)._compute_meeting_count()
        meeting_data = self.env['calendar.event'].read_group([('opportunity_id', 'in', self.ids),('editable','=',False)],
                                                             ['opportunity_id'],
                                                             ['opportunity_id'])
        mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = lead.meeting_count - mapped_data.get(lead.id, 0)

    @api.multi
    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()

        action = super(Lead, self).action_schedule_meeting()
        action['context']['default_partner_ids'] = self.env.user.partner_id.ids

        if self.partner_id:
            if self.partner_id.is_company:
                name = "{} - {} ".format(self.partner_id.commercial_company_name,
                                         self.name)
            else:
                if self.partner_id.commercial_company_name:
                    contacts = "{}, {}".format(self.partner_id.commercial_company_name,
                                           self.partner_id.name)
                else:
                    contacts = self.partner_id.name

                name = "{} - {} ".format(contacts, self.name)

            action['context']['default_res_id'] = self.id
            action['context']['default_res_model'] = 'crm.lead'
            action['context']['default_name'] = name
            # action['context']['search_default_partner_ids'] = self.partner_id.name
        return action
