from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
    validation_requested = fields.Boolean(string="Validation requested",
                                          readonly=True)
    validated = fields.Boolean(string="Validation request",
                               readonly=True)
    validation_date = fields.Date(string="Validation date",
                                  readonly=True)
    validated_by = fields.Many2one('res.users',
                                   string="Validated by",
                                   readonly=True)
    state = fields.Selection([('open', 'Open'),
                              ('close', 'Close'),
                              ('waiting', 'Waiting list')],
                             string="State",
                             default='close')
    solidary = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string="Solidary product")
    banking = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')],
                               string="Banking product")
    book_value = fields.Float(string="Book value",
                              translate=True)
    dividend_policy = fields.Html(string="Dividend policy",
                                  translate=True)
    voting_rights = fields.Html(string="Voting rights",
                                help="Voting rights of the associate",
                                translate=True)
    advantages = fields.Html(string="Other advantages",
                             translate=True)
    tax_policy = fields.Char(string="Tax policy",
                             translate=True)
    tax_benefit = fields.Char(string="Tax benefit",
                              translate=True)
    fees = fields.Html(string="Subscription_fees",
                       translate=True)
    minimum_amount = fields.Monetary(string="Minimum subscription amount",
                                     currency_field='currency_id')
    maximum_amount = fields.Monetary(string="Maximum subscription amount",
                                     currency_field='currency_id')
    access_terms = fields.Char(string="Terms of access",
                               translate=True)
    max_target_issue = fields.Monetary(string="Issue total amount",
                                       currency_field='currency_id')
    min_target_issue = fields.Monetary(string="Issue minimal amount",
                                       currency_field='currency_id')
    subscription_start_date = fields.Date(string="Issue Start date")
    subscription_end_date = fields.Date(string="Issue End date")
    subscription_length = fields.Char(string="Subscription length",
                                      translate=True)
    oversubscription_policy = fields.Char(string="Over subscription policy",
                                          translate=True)
    purpose_of_issue = fields.Html(string="Purpose of the issue",
                                   translate=True)
    price_fluctuation_risk = fields.Char(string="Price fluctuation risk",
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
    def count_published_shares(self):
        """Count number of share type that investor can invest in"""
        return self.search_count([
            ("is_share", "=", True),
            ("sale_ok", "=", True),
            ("state", "=", "open"),
            ("display_on_website", "=", True),
        ])

    @api.multi
    def validation_request(self):
        for product in self:
            product.validation_requested = True

    @api.multi
    def validate(self):
        for product in self:
            product.write({'validated': True,
                           'display_on_website': True,
                           'validation_date': fields.Date.today(),
                           'validated_by': self.env.user.id
                           })

    @api.multi
    def refuse(self):
        for product in self:
            product.validation_requested = False

    @api.multi
    def can_buy_max_amount(self, partner_id):
        """
        Return the amount that a partner can subscribe on for this type
        of share product.
        Return a negative number if there is not limit.
        """
        self.ensure_one()
        company = self.env["res.company"]._company_default_get()
        amount_owned_structure = partner_id.owned_structure_amount(
            self.structure, manual=True
        )
        amount_owned_share = partner_id.owned_amount(self, manual=True)
        max_subscription = (
            self.structure.subscription_maximum_amount
            or company.subscription_maximum_amount
        )
        # Actual amount regarding to the general max subscription
        actual_struct_max = None
        if max_subscription > 0:
            # Set actual structure max if there is a general maximum
            actual_struct_max = max(
                0, max_subscription - amount_owned_structure,
            )
        # Actual amount for this type of share
        actual_share_max = None
        if self.maximum_amount > 0:
            # Set actual share max if there is one
            actual_share_max = max(0, self.maximum_amount - amount_owned_share)
        # Choose which maximum to return
        if actual_struct_max is not None and actual_share_max is not None:
            return min(actual_struct_max, actual_share_max)
        if actual_share_max is not None:
            return actual_share_max
        if actual_struct_max is not None:
            return actual_struct_max
        return -1  # No limit

    @api.multi
    def can_buy_min_amount(self, partner_id):
        """
        Return the minimum amount that a partner have to subscribe.
        """
        self.ensure_one()
        return max(
            0, self.minimum_amount - partner_id.owned_amount(self, manual=True)
        )
