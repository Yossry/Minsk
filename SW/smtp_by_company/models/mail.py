# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
#################################################################################

from odoo import fields, models, api

class Mail(models.Model):

    _inherit = "mail.mail"

    @api.model
    def create(self, vals):

        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context.get('uid'))
            if user:
                out_mail_sever = self.env['ir.mail_server'].search([('company_id', '=', user.company_id.id)], limit=1)
                if out_mail_sever:
                    email_from = user.partner_id.name + " " + "<" + out_mail_sever.smtp_user + ">"
                    reply_to   = user.partner_id.name + " " + "<" +user.partner_id.email or out_mail_sever.smtp_user
                    vals.update({'mail_server_id':out_mail_sever.id, 'email_from':email_from, 'reply_to':reply_to })
        result = super(Mail, self).create(vals)
        return result

class MailMessage(models.Model):

    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        active_company_id = self.env.user.company_id and self.env.user.company_id.id
        out_mail_sever = self.env['ir.mail_server'].sudo().search([('company_id', '=', active_company_id)])
        if out_mail_sever:
            vals.update({'mail_server_id':out_mail_sever.id})
        result = super(MailMessage, self).create(vals)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





