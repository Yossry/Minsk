from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)

    def get_structure_email_template_notif(self, is_company=False):
        if is_company:
            mail_template = 'investor_wallet_platform_base.email_template_notification_company'
        else:
            mail_template = 'investor_wallet_platform_base.email_template_notification'
        return self.env.ref(mail_template, False)

    def get_mail_template_notif(self, is_company=False):
        templ_obj = self.env['mail.template']
        if is_company:
            return templ_obj.get_email_template_by_key('sub_req_comp_notif',
                                                       self.structure)
        else:
            return templ_obj.get_email_template_by_key('sub_req_notif',
                                                       self.structure)

    def get_capital_release_mail_template(self):
        template_obj = self.env['mail.template']
        return template_obj.get_email_template_by_key('rel_capital',
                                                      self.structure)
    @api.model
    def create(self, vals):
        subscr_request = super(SubscriptionRequest, self).create(vals)
        notification_template = subscr_request.get_structure_email_template_notif(False)
        notification_template.send_mail(subscr_request.id)
        return subscr_request

    @api.model
    def create_comp_sub_req(self, vals):
        subscr_request = super(SubscriptionRequest, self).create_comp_sub_req(vals)
        notification_template = subscr_request.get_structure_email_template_notif(True)
        notification_template.send_mail(subscr_request.id)
        return subscr_request

    def get_journal(self):
        if self.structure:
            if self.structure.account_journal:
                return self.structure.account_journal
            else:
                raise ValidationError(_('There is no journal defined for this '
                                        'structure.'))
        else:
            raise ValidationError(_('There is no structure defined on this '
                                    'subscription request.'))

    def get_invoice_vals(self, partner):
        vals = super(SubscriptionRequest, self).get_invoice_vals(partner)
        vals['structure'] = self.structure.id

        return vals

    def is_member(self, vals, cooperator):
        membership = cooperator.get_membership(self.structure)

        if membership and membership.member:
            vals['type'] = 'increase'
            vals['already_cooperator'] = True
        return vals

    def set_membership(self):
        member_obj = self.env['coop.membership']
        membership = self.partner_id.get_membership(self.structure)
        if not membership:
            vals = {'structure': self.structure.id,
                    'partner_id': self.partner_id.id
                    }
            member_obj.create(vals)
        return True


class ShareLine(models.Model):
    _inherit = 'share.line'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
    creation_mode = fields.Selection(
        [('auto', 'Automatic'), ('manual', 'Manual')],
        string="Creation mode",
        default='auto',
        readonly=True,
        help=(
            "'auto' means created by system, 'manual' means manually "
            "created by a user."
        ),
    )


class SubscriptionRegister(models.Model):
    _inherit = 'subscription.register'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)


class OperationRequest(models.Model):
    _inherit = 'operation.request'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)

    def get_share_trans_mail_template(self):
        templ_obj = self.env['mail.template']
        return templ_obj.get_email_template_by_key('certificate_trans',
                                                   self.structure)

    def get_share_update_mail_template(self):
        templ_obj = self.env['mail.template']
        return templ_obj.get_email_template_by_key('share_update',
                                                   self.structure)

    def send_share_trans_mail(self, sub_register_line):
        cert_email_template = self.get_share_trans_mail_template()
        # TODO this will need a dedicated certificate report
        cert_email_template.send_mail(sub_register_line.id, False)

    def send_share_update_mail(self, sub_register_line):
        cert_email_template = self.get_share_update_mail_template()
        cert_email_template.send_mail(sub_register_line.id, False)

    def get_subscription_register_vals(self, effective_date):
        vals = super(OperationRequest, self).get_subscription_register_vals(effective_date)
        vals['structure'] = self.structure.id
        return vals

    def get_total_share_dic(self, partner):
        share_products = self.env['product.template'].search(
            [('is_share', '=', True), ("structure", "=", self.structure.id)]
        )
        # Init total_share_dic
        total_share_dic = {}
        for share_product in share_products:
            total_share_dic[share_product.id] = 0

        shares = partner.share_ids.filtered(
            lambda r: (
                r.structure == self.structure and r.creation_mode == "auto"
            )
        )
        for line in shares:
            total_share_dic[line.share_product_id.id] += line.share_number
        return total_share_dic


    def hand_share_over(self, partner, share_product_id, quantity):
        membership = partner.get_membership(self.structure)
        if not membership.member:
            raise ValidationError(_("This operation can't be executed if the"
                                    " cooperator is not an effective member"))

        owned_shares = partner.share_ids.filtered(
            lambda r: (
                r.structure == self.structure and r.creation_mode == "auto"
            )
        )
        share_ind = len(owned_shares)
        i = 1
        while quantity > 0:
            line = owned_shares[share_ind - i]
            if line.share_product_id.id == share_product_id.id:
                if quantity > line.share_number:
                    quantity -= line.share_number
                    line.unlink()
                else:
                    share_left = line.share_number - quantity
                    quantity = 0
                    line.write({'share_number': share_left})
            i += 1
        # if the cooperator sold all his shares he's no more
        # an effective member
        remaning_share_dict = 0
        for share_quant in self.get_total_share_dic(partner).values():
            remaning_share_dict += share_quant
        if remaning_share_dict == 0:
            membership.write({'member': False, 'old_member': True})
