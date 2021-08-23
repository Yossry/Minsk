# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if partner and not partner.user_ids and self.env['ir.config_parameter'].get_param('portal_remove_mail_footer.portal', '1') != '0':
            #Portal footer
            return super(MailMail, self)._get_partner_access_link(mail, partner=partner)
        if partner and partner.user_ids and self.env['ir.config_parameter'].get_param('portal_remove_mail_footer.mail', '1') != '0':
            #Mail footer
            return super(MailMail, self)._get_partner_access_link(mail, partner=partner)
        else:
            return None

#~ class MailNotification(models.Model):
    #~ _name = 'mail.notification'

    #~ def get_signature_footer(self, cr, uid, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        #~ """ Format a standard footer for notification emails (such as pushed messages
            #~ notification or invite emails).
            #~ Format:
                #~ <p>--<br />
                    #~ Administrator
                #~ </p>
                #~ <div>
                    #~ <small>Sent from <a ...>Your Company</a> using <a ...>OpenERP</a>.</small>
                #~ </div>
        #~ """
        #~ footer = ""
        #~ if not user_id:
            #~ return footer

        #~ # add user signature
        #~ user = self.pool.get("res.users").browse(cr, SUPERUSER_ID, [user_id], context=context)[0]
        #~ if user_signature:
            #~ if user.signature:
                #~ signature = user.signature
            #~ else:
                #~ signature = "--<br />%s" % user.name
            #~ footer = tools.append_content_to_html(footer, signature, plaintext=False)

        #~ # add company signature
        #~ if user.company_id.website:
            #~ website_url = ('http://%s' % user.company_id.website) if not user.company_id.website.lower().startswith(('http:', 'https:')) \
                #~ else user.company_id.website
            #~ company = "<a style='color:inherit' href='%s'>%s</a>" % (website_url, user.company_id.name)
        #~ else:
            #~ company = user.company_id.name
        #~ sent_by = _('Sent by %(company)s using %(odoo)s')

        #~ signature_company = '<br /><small>%s</small>' % (sent_by % {
            #~ 'company': company,
            #~ 'odoo': "<a style='color:inherit' href='https://www.odoo.com/'>Odoo</a>"
        #~ })
        #~ footer = tools.append_content_to_html(footer, signature_company, plaintext=False, container_tag='div')

        #~ return footer
