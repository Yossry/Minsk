###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def add_email_blacklist(self):
        for record in self:
            self.env['mail.blacklist']._add(record.email)
            record.message_post(
                body=_('Email added to blacklist.')
            )

    def remove_email_blacklist(self):
        for record in self:
            self.env['mail.blacklist']._remove(record.email)
            record.message_post(
                body=_('Email removed from the blacklist.')
            )
