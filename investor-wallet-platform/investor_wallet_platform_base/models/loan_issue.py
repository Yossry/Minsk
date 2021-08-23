# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LoanIssue(models.Model):
    _inherit = "loan.issue"

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name="res.partner",
                                string="Platform Structure",
                                domain=[("is_platform_structure", "=", True)],
                                default=default_structure,
                                )
    validation_requested = fields.Boolean(string="Validation requested",
                                          readonly=True)
    validated = fields.Boolean(string="Validation request",
                               readonly=True)
    validation_date = fields.Date(string="Validation date",
                                  readonly=True)
    validated_by = fields.Many2one('res.users',
                                   string="Validated by",
                                   readonly=True)
    solidary = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string="Solidary product")
    banking = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')],
                               string="Banking product")
    book_value = fields.Html(string="Book value",
                             translate=True)
    advantages = fields.Html(string="Other advantages",
                             translate=True)
    tax_policy = fields.Char(string="Tax policy",
                             translate=True)
    tax_benefit = fields.Char(string="Tax benefit",
                              translate=True)
    fees = fields.Html(string="Subscription_fees",
                       translate=True)
    access_terms = fields.Char(string="Access terms",
                                      translate=True)
    oversubscription_policy = fields.Char(string="Over subscription policy",
                                          translate=True)
    purpose_of_issue = fields.Html(string="Purpose of the issue",
                                   translate=True)
    price_fluctuation_risk = fields.Char(string="Price fluctuation price",
                                         translate=True)
    capital_risk = fields.Html(string="Risk on equity",
                               translate=True)
    other_product_risk = fields.Html(string="Other risk on product",
                                     translate=True)
    transfer_allowed = fields.Html(string="Product transfer possibility",
                                   translate=True)
    refund_policy = fields.Html(string="Refund policy",
                                translate=True)
    info_note_url = fields.Char(string="Information note url")

    @api.model
    def count_published_loans(self):
        """Count number of loan issue that investor can invest in"""
        return self.search_count([
            ("state", "=", "ongoing"),
            ("display_on_website", "=", True),
        ])

    @api.multi
    def validation_request(self):
        for issue in self:
            issue.validation_requested = True

    @api.multi
    def validate(self):
        for issue in self:
            issue.write({'validated': True,
                         'display_on_website': True,
                         'validation_date': fields.Date.today(),
                         'validated_by': self.env.user.id
                         })

    @api.multi
    def refuse(self):
        for issue in self:
            issue.validation_requested = False


class LoanIssueLine(models.Model):
    _inherit = "loan.issue.line"

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        related="loan_issue_id.structure",
        store=True,
    )
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

    def get_loan_sub_mail_template(self):
        template_obj = self.env['mail.template']
        return template_obj.get_email_template_by_key('loan_sub_conf',
                                                      self.structure)

    def get_loan_pay_req_mail_template(self):
        template_obj = self.env['mail.template']
        return template_obj.get_email_template_by_key('loan_payment_req',
                                                      self.structure)
