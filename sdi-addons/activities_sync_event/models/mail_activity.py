# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, tools, _


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_feedback(self, feedback=False):
        """
        Override.
        If a meeting-type activity has been marked as done,
        the related event is also marked as not editable.
        :param feedback:
        :return:
        """
        events = self.mapped('calendar_event_id')
        res = super(MailActivity, self).action_feedback(feedback)
        for event in events:
            event.editable = False
        return res

    @api.multi
    def action_create_calendar_event(self):
        """
        Modified functionality of the method:
        Add customer's contact and user to meeting through 'default_partners_ids'.
        :return: action
        """
        self.ensure_one()
        action = super(MailActivity,self).action_create_calendar_event()
        name = action['context'].get('default_name', False)

        # crm.lead
        if action['context'].get('default_res_id') and \
            action['context']['default_res_model'] == 'crm.lead':
            lead = self.env['crm.lead'].browse(int(action['context']['default_res_id']))
            if lead.id and lead.type == 'opportunity':
                action['context']['default_opportunity_id'] = lead.id

            name = "{} - {}".format(lead.name, name)
            action['context']['default_name'] = name

        partner_ids = self.env.user.partner_id.ids
        # add customer to meeting like attendee
        customer = self._get_customer(action['context'])
        # if customer.id:
        #     partner_ids.append(customer.id)
        action['context']['default_partner_ids'] = partner_ids

        # If we know customer, his name will put in tittle of meeting
        self._add_partner_to_meeting_name(action['context'], name, customer)

        #res.partner
        # if action['context']['default_res_model'] == 'res.partner':
        #     action['context']['search_default_partner_ids'] = customer.name

        return action


    def _add_partner_to_meeting_name(self, context, name, customer):
        if customer and customer.id:
            if customer.is_company and name:
                name = "{} - {} ".format(customer.commercial_company_name, name)
            elif customer.is_company:
                name = "{}".format(customer.commercial_company_name)
            elif not customer.is_company:
                if customer.parent_id.id and customer.parent_id.commercial_company_name:
                    contacts = "{}, {}".format(customer.commercial_company_name,
                                           customer.name)
                else:
                    contacts = customer.name
                if name:
                    name = "{} - {} ".format(contacts, name)
                else:
                    name = contacts
        context['default_name'] = name


    def _get_customer(self,context):
        customer = None
        if context['default_res_model'] == 'res.partner' and context['default_res_id']:
            customer = self.env['res.partner'].browse(context['default_res_id'])
        elif context['default_res_model'] and context['default_res_id']:
            obj = self.env[context['default_res_model']].browse(context['default_res_id'])
            model = self.env[context['default_res_model']].with_context(active_test=False)
            if 'partner_id' in model._fields and obj.partner_id:
                customer = obj.partner_id
        return customer
