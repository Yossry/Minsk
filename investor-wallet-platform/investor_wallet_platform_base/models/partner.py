# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _

from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def default_structure(self):
        return self.env.user.structure

    @api.multi
    @api.depends('share_ids')
    def _compute_cooperator_type(self):
        for partner in self:
            partner.cooperator_type = 'none'

    is_platform_structure = fields.Boolean(string="Is a Platform Structure")
    cooperator_type = fields.Selection(selection=[('none', 'None')],
                                       compute=_compute_cooperator_type,
                                       string='Cooperator Type',
                                       store=True)
    coop_membership = fields.One2many('coop.membership',
                                      'partner_id',
                                      string="Cooperative membership")
    state = fields.Selection([('draft', 'Draft'),
                              ('refused', 'Refused'),
                              ('to_validate', 'Need validation'),
                              ('validated', 'Validated')],
                             string="State",
                             default='draft')
    validation_date = fields.Date(string="Validation date",
                                  readonly=True)
    validated_by = fields.Many2one('res.users',
                                   string="Validated by",
                                   readonly=True)
    initialized = fields.Boolean(string="Sequence initialized")
    structure_type = fields.Selection([('cooperative', 'Cooperative'),
                                       ('association', 'Association'),
                                       ('limited_company', 'Limited Company')],
                                      string="Structure type")
    structure_type_value = fields.Char(compute='_return_structure_type_value',
                                       string="Structure type")
    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
    account_journal = fields.Many2one('account.journal',
                                      string="Account Journal",
                                      readonly=True)
    register_sequence = fields.Many2one('ir.sequence',
                                        string="Register sequence",
                                        readonly=True)
    operation_sequence = fields.Many2one('ir.sequence',
                                         string="Operation Register",
                                         readonly=True)
    share_type_ids = fields.One2many("product.template",
                                     "structure",
                                     string="Share type")
    loan_issue_ids = fields.One2many("loan.issue",
                                     "structure",
                                     string="Loan issues")
    mail_template_ids = fields.One2many("mail.template",
                                        "structure",
                                        string="Mail templates")
    projects = fields.Html(string="Projects",
                           translate=True)
    display_on_website = fields.Boolean(string="display on website")
    board_representative = fields.Char(string="Board representative name")
    signature_scan = fields.Binary(string="Board representative signature")
    # Move to another module ?
    is_renewable_energy = fields.Boolean(string="is renewable energy")
    renewable_energy = fields.Html(string="Renewable energy",
                                   translate=True)
    description = fields.Html(string="Description",
                              translate=True)
    about_us = fields.Html(string="About us",
                           translate=True)
    governance = fields.Html(string="Governance",
                             translate=True)
    cover_image = fields.Binary(string="Cover image",
                                translate=True)
    labour_on_capital = fields.Html(string="Labour on capital",
                                    translate=True)
    autonomy_of_management = fields.Html(string="Autonomy of management",
                                         translate=True)
    purpose_service = fields.Html(string="Purpose of service to members",
                                  translate=True)
    sustainable_development = fields.Html(string="Sustainable development",
                                          translate=True)
    key_numbers = fields.Html(string="Key Numbers",
                              translate=True)
    operational_risk = fields.Html(string="Operational & commercial risk",
                                   translate=True)
    governance_risk = fields.Html(string="Governance risk",
                                  translate=True)
    total_bs = fields.Char(string="Total balance sheet",
                           translate=True)
    equity = fields.Html(string="Equity",
                         translate=True)
    solvency_ratio = fields.Html(string="Solvency ratio",
                                 translate=True)
    last_result = fields.Html(string="Last result",
                              translate=True)
    last_dividend = fields.Html(string="Last 3 years dividend",
                                translate=True)
    break_even_date = fields.Date(string="Break-even date")
    liquidity_ratio = fields.Html(string="Liquidity ratio",
                                  translate=True)
    susbidies_risk = fields.Html(string="Risks related to subsidies",
                                 translate=True)
    subscription_maximum_amount = fields.Monetary(
        string="Maximum authorised subscription amount",
        currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency',
                                          related='company_id.currency_id',
                                          string="Company Currency",
                                          readonly=True)
    approval = fields.Char(string="Approval",
                           translate=True)
    activity_areas = fields.Many2many('activity.area',
                                      string="Activity areas")
    employee_number = fields.Char(string="Employee number",
                                  translate=True)
    statute_link = fields.Char(string="Statute link")
    annual_report_link = fields.Char(string="Last annual report link")
    area_char_list = fields.Char(compute='_return_area_char_list',
                                 string="activity areas")
    mail_serveur_out = fields.Many2one('ir.mail_server',
                                       string="Mail serveur out")
    industry_char_list = fields.Char(compute='_return_industry_char_list')
    can_subscribe = fields.Boolean(
        string="Can be subscribed ?",
        compute='_can_subscribe_products')
    total_outstanding_amount = fields.Monetary(
        string="Total Outsanding Amount"
    )
    data_policy_approval_text = fields.Html(
        translate=True,
        default="I approve the data policy.",
        help="Text to display aside the checkbox to approve data policy."
    )
    internal_rules_approval_text = fields.Html(
        translate=True,
        default="I approve internal rules.",
        help="Text to display aside the checkbox to approve internal rules."
    )
    financial_risk_approval_text = fields.Html(
        translate=True,
        default="I aware of financial risk.",
        help="Text to display aside the checkbox to approve financial risk."
    )

    structure_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='iwp_res_partner_structure_rel',
        column1='partner_id',
        column2='structure_id',
        string='Linked to Structures',
        compute='_compute_linked_structure',
        store=True,
        help="Used to restrict access in views",
    )
    membership_structure_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='iwp_res_partner_membership_rel',
        column1='partner_id',
        column2='structure_id',
        string='Member of Structures',
        compute='_compute_structure_membership',
        store=True,
        help="Used to restrict access in views",
    )
    candidate_structure_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='iwp_res_partner_candidate_rel',
        column1='partner_id',
        column2='structure_id',
        string='Candidate for Structures',
        compute='_compute_structure_membership',
        store=True,
        help="Used to restrict access in views",
    )
    old_member_structure_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='iwp_res_partner_old_member_rel',
        column1='partner_id',
        column2='structure_id',
        string='Old Member of Structures',
        compute='_compute_structure_membership',
        store=True,
        help="Used to restrict access in views",
    )
    loan_structure_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='iwp_res_partner_loan_rel',
        column1='partner_id',
        column2='structure_id',
        string='Loaned to Structures',
        compute='_compute_structure_loans',
        store=True,
        help="Used to restrict access in views",
    )

    @api.multi
    @api.depends('coop_membership.structure',
                 'loan_line_ids.structure')
    def _compute_linked_structure(self):
        for partner in self:
            coop_structure_ids = (
                partner.coop_membership
                       .mapped('structure')
                       .ids
            )
            loan_structure_ids = (
                partner
                .loan_line_ids
                .mapped('structure')
                .ids
            )
            partner.structure_ids = coop_structure_ids + loan_structure_ids

    @api.multi
    @api.depends('coop_membership.structure',
                 'coop_membership.member',
                 'coop_membership.coop_candidate',
                 'coop_membership.old_member')
    def _compute_structure_membership(self):
        for partner in self:
            member_structure_ids = (
                partner.coop_membership
                       .filtered(lambda cm: cm.member)
                       .mapped('structure')
                       .ids
            )
            partner.membership_structure_ids = member_structure_ids
            candidate_structure_ids = (
                partner.coop_membership
                       .filtered(lambda cm: cm.coop_candidate)
                       .mapped('structure')
                       .ids
            )
            partner.candidate_structure_ids = candidate_structure_ids
            old_member_structure_ids = (
                partner.coop_membership
                       .filtered(lambda cm: cm.old_member)
                       .mapped('structure')
                       .ids
            )
            partner.old_member_structure_ids = old_member_structure_ids

    @api.multi
    @api.depends('loan_line_ids.structure')
    def _compute_structure_loans(self):
        for partner in self:
            loan_structure_ids = (
                partner
                .loan_line_ids
                .mapped('structure')
                .ids
            )
            partner.loan_structure_ids = loan_structure_ids

    def _get_structure_type_value(self, field_desc, structure_type):
        for desc in field_desc:
            if desc[0] == structure_type:
                return desc[1]
        return False

    @api.multi
    def _return_structure_type_value(self):
        desc = self.env['res.partner'].sudo().fields_get(['structure_type'])
        field_desc = desc['structure_type']['selection']
        for partner in self:
            value = self._get_structure_type_value(field_desc,
                                                   partner.structure_type)
            partner.structure_type_value = value

    @api.multi
    def _return_area_char_list(self):
        for partner in self:
            partner.area_char_list = partner.activity_areas.mapped('name')

    @api.multi
    def _return_industry_char_list(self):
        for partner in self:
            partner.industry_char_list = (
                    partner
                    .industry_id
                    .mapped('full_name')
            )

    @api.multi
    def _can_subscribe_products(self):
        for partner in self:
            if partner.share_type_ids.filtered(
                    lambda r: r.display_on_website and r.state != 'close'):
                partner.can_subscribe = True
            if partner.loan_issue_ids.filtered(
                    lambda r: r.display_on_website and r.state != 'closed'):
                partner.can_subscribe = True

    @api.multi
    def generate_sequence(self):
        self.ensure_one()
        journal_obj = self.env['account.journal']
        ir_sequence_obj = self.env['ir.sequence']

        if not self.initialized:
            sequence_vals = {
                'name': 'Subscription Register ' + self.name,
                'code': 'subscription.register.' + self.name.replace(" ", "_"),
                'number_next': 1,
                'number_increment': 1,
            }
            register_sequence = ir_sequence_obj.create(sequence_vals)

            sequence_vals = {
                'name': 'Register Operation ' + self.name,
                'code': 'register.operation.' + self.name.replace(" ", "_"),
            }
            operation_sequence = ir_sequence_obj.create(sequence_vals)
            sequence_vals = {
                'name': 'Account Default Subscription Journal ' + self.name,
                'padding': 3,
                'use_date_range': True,
                'prefix': 'SUBJ/%(year)s/',
            }
            journal_sequence = ir_sequence_obj.create(sequence_vals)
            # TODO create journal
            journal_vals = {
                'name': 'Subscription Journal ' + self.name,
                'code': 'SUBJ_' + self.name.replace(" ", "_"),
                'type': 'sale',
                'sequence_id': journal_sequence.id,
            }
            account_journal = journal_obj.create(journal_vals)
            self.register_sequence = register_sequence
            self.operation_sequence = operation_sequence
            self.account_journal = account_journal
            self.initialized = True
        else:
            raise UserError(_('You cannot initialize an already initialized '
                              'structure'))
        return True

    def get_membership(self, structure):
        return self.coop_membership.filtered(
            lambda record: record.structure == structure
        )

    @api.multi
    def generate_mail_templates(self):
        self.ensure_one()
        if self.mail_serveur_out:
            mail_templ = self.env['mail.template']._get_email_template_dict()

            if not self.mail_template_ids:
                for mt_key, mt_xml_id in mail_templ.items():
                    mail_template = self.env.ref(mt_xml_id, False)
                    struct_mail_template = mail_template.copy(default={
                        'mail_server_id': self.mail_serveur_out.id,
                        'structure': self.id,
                        'template_key': mt_key
                    })
                    struct_mail_template.name = mail_template.name
        else:
            raise UserError(_('You need first to define a mail server out'))

    @api.multi
    def validation_request(self):
        for partner in self:
            partner.state = 'to_validate'

    @api.multi
    def validate(self):
        for partner in self:
            partner.write({'state': 'validated',
                           'display_on_website': True,
                           'validation_date': fields.Date.today(),
                           'validated_by': self.env.user.id
                           })

    @api.multi
    def refuse(self):
        for partner in self:
            partner.state = 'refused'

    def send_mail_notif(self):
        template = self.env.ref(
            'investor_wallet_platform_base.email_template_structure_updated',
            False
        )
        template.sudo().send_mail(self.id)
        return True

    @api.multi
    def write(self, vals):
        for partner in self:
            if partner.is_platform_structure:
                # the web client return default html tags for
                # empty html fields. So we remove it from the vals
                keys_to_delete = []
                for key in vals.keys():
                    if vals.get(key) == '<p><br></p>':
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    vals.pop(key)
                result = super(ResPartner, partner).write(vals)
                if partner.changeset_ids:
                    partner.send_mail_notif()
                    partner.changeset_ids.unlink()
            else:
                result = super(
                    ResPartner, partner.with_context(__no_changeset=True)
                ).write(vals)
        return result

    @api.multi
    def owned_amount(self, share_type, manual=False):
        """
        Return the amount of share_type owned by this cooperator.
        If manual is set to True, then manual share lines are taken into
        account.
        """
        self.ensure_one()
        lines = (
            sl
            for sl in self.share_ids
            if sl.share_product_id == share_type.product_variant_id
        )
        if not manual:
            # Remove manual share lines
            lines = (sl for sl in lines if sl.creation_mode != "manual")
        owned = sum(sl.total_amount_line for sl in lines)
        pending_sub = self.env["subscription.request"].search(
            [
                ("partner_id", "=", self.id),
                ("share_product_id", "=", share_type.product_variant_id.id),
                ("state", "!=", "paid"),
                ("state", "!=", "cancelled"),
                ("state", "!=", "transfer"),
            ]
        )
        pending_op = self.env["operation.request"].search(
            [
                ("partner_id", "=", self.id),
                ("share_product_id", "=", share_type.product_variant_id.id),
                ("state", "!=", "refused"),
                ("state", "!=", "cancelled"),
                "|",
                ("operation_type", "=", "transfert"),
                ("operation_type", "=", "sell_back"),
            ]
        )
        amount_pending_sub = sum(sr.subscription_amount for sr in pending_sub)
        amount_pending_op = sum(op.subscription_amount for op in pending_op)
        return owned + amount_pending_sub - amount_pending_op

    @api.multi
    def owned_structure_amount(self, structure, manual=False):
        """
        Return the amount owned by this cooperator in the given structure.
        """
        self.ensure_one()
        lines = (sl for sl in self.share_ids if sl.structure == structure)
        if not manual:
            # Remove manual share lines
            lines = (sl for sl in lines if sl.creation_mode != "manual")
        owned = sum(sl.total_amount_line for sl in lines)
        pending_sub = self.env["subscription.request"].search(
            [
                ("partner_id", "=", self.id),
                ("structure", "=", structure.id),
                ("state", "!=", "paid"),
                ("state", "!=", "cancelled"),
                ("state", "!=", "transfer"),
            ]
        )
        pending_op = self.env["operation.request"].search(
            [
                ("partner_id", "=", self.id),
                ("structure", "=", structure.id),
                ("state", "!=", "refused"),
                ("state", "!=", "cancelled"),
                "|",
                ("operation_type", "=", "transfert"),
                ("operation_type", "=", "sell_back"),
            ]
        )
        amount_pending_sub = sum(sr.subscription_amount for sr in pending_sub)
        amount_pending_op = sum(op.subscription_amount for op in pending_op)
        return owned + amount_pending_sub - amount_pending_op
