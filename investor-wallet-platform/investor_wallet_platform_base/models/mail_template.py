from odoo import fields, models

_EMAIL_TEMPLATE_IDS = {
    "sub_req_notif": "investor_wallet_platform_base.email_template_confirmation",
    "sub_req_comp_notif": "investor_wallet_platform_base.email_template_confirmation_company",
    "rel_capital": "investor_wallet_platform_base.email_template_release_capital",
    "certificate": "investor_wallet_platform_base.email_template_certificat",
    "certificate_inc": "investor_wallet_platform_base.email_template_certificat_increase",
    "certificate_trans": "investor_wallet_platform_base.email_template_share_transfer",
    "share_update": "investor_wallet_platform_base.email_template_share_update",
    "loan_sub_conf": "investor_wallet_platform_base.loan_subscription_confirmation",
    "loan_payment_req": "investor_wallet_platform_base.loan_issue_payment_request",
    }


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _get_email_template_dict(self):
        return _EMAIL_TEMPLATE_IDS

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)])
    template_key = fields.Char(string="Mail template key",
                               readonly=True)
    iwp = fields.Boolean(string="IWP mail template")

    def get_email_template_by_key(self, mail_template_key, structure):
        template_obj = self.env['mail.template']
        mail_template = template_obj.search([
                            ('template_key', '=', mail_template_key),
                            ('structure', '=', structure.id)])
        return mail_template
