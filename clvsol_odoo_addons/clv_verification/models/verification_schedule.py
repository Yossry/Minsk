# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VerificationSchedule(models.Model):
    _description = 'Verification Schedule'
    _name = 'clv.verification.schedule'
    _order = 'name'

    template_id = fields.Many2one(
        comodel_name='clv.verification.template',
        string='Verification Template',
        required=False,
        ondelete='restrict'
    )

    name = fields.Char(
        string='Name',
        required=True,
        help='Verification Schedule Name'
    )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    date_last_verification = fields.Datetime(
        string='Last Verification Date',
        readonly=True
    )

    model = fields.Char(
        string='Model',
        required=False,
        help="Model name of the object on which the verification method to be called is located, e.g. 'res.partner'"
    )

    method = fields.Char(
        string='Method',
        required=False,
        help="Name of the method to be called when the verification job is processed."
    )

    action = fields.Char(
        string='Action',
        required=False,
        help="Name of the action used to process the verification."
    )

    verification_max_task = fields.Integer(
        string='Max Task Registers'
    )

    verification_disable_identification = fields.Boolean(
        string='Disable Identification'
    )

    verification_disable_check_missing = fields.Boolean(
        string='Disable Check Missing'
    )

    verification_disable_inclusion = fields.Boolean(
        string='Disable Inclusion'
    )

    verification_disable_verification = fields.Boolean(
        string='Disable Verification'
    )

    verification_last_update_start = fields.Datetime(
        string="Last Update (Start)"
    )

    verification_last_update_end = fields.Datetime(
        string="Last Update (End)"
    )

    verification_log = fields.Text(
        string="Verification Log"
    )

    active = fields.Boolean(string='Active', default=1)

    date_last_verification = fields.Datetime(
        string='Last Verification Date',
        readonly=True
    )
    upmost_last_update = fields.Datetime(
        string="Upmost Last Update",
        readonly=True
    )

    # _sql_constraints = [
    #     ('name_uniq',
    #      'UNIQUE (name)',
    #      u'Error! The Name must be unique!'),
    # ]

    @api.model
    def create(self, values):

        schedule = super().create(values)

        if schedule.template_id.id is not False:

            schedule.verification_max_task = schedule.template_id.verification_max_task
            schedule.verification_disable_identification = schedule.template_id.verification_disable_identification
            schedule.verification_disable_check_missing = schedule.template_id.verification_disable_check_missing
            schedule.verification_disable_inclusion = schedule.template_id.verification_disable_inclusion
            schedule.verification_disable_verification = schedule.template_id.verification_disable_verification
            schedule.verification_last_update_start = schedule.template_id.verification_last_update_start
            schedule.verification_last_update_end = schedule.template_id.verification_last_update_end
            schedule.model = schedule.template_id.model
            schedule.method = schedule.template_id.method
            schedule.action = schedule.template_id.action

        return schedule

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id.id:

            self.verification_max_task = self.template_id.verification_max_task
            self.verification_disable_identification = self.template_id.verification_disable_identification
            self.verification_disable_check_missing = self.template_id.verification_disable_check_missing
            self.verification_disable_inclusion = self.template_id.verification_disable_inclusion
            self.verification_disable_verification = self.template_id.verification_disable_verification
            self.verification_last_update_start = self.template_id.verification_last_update_start
            self.verification_last_update_end = self.template_id.verification_last_update_end
            self.model = self.template_id.model
            self.method = self.template_id.method
            self.action = self.template_id.action

    @api.model
    def verification_last_update_args(self):

        args = []
        if self.verification_last_update_start is not False and \
           self.verification_last_update_end is False:
            args = [('write_date', '>=', self.verification_last_update_start), ]
        if self.verification_last_update_start is False and \
           self.verification_last_update_end is not False:
            args += [('write_date', '<=', self.verification_last_update_end), ]
        if self.verification_last_update_start is not False and \
           self.verification_last_update_end is not False:
            args += [('write_date', '>=', self.verification_last_update_start),
                     ('write_date', '<=', self.verification_last_update_end), ]

        return args


class VerificationTemplate(models.Model):
    _inherit = 'clv.verification.template'

    schedule_ids = fields.One2many(
        comodel_name='clv.verification.schedule',
        inverse_name='template_id',
        string='Schedules'
    )
    count_schedules = fields.Integer(
        string='Number of Schedules',
        compute='_compute_count_schedules',
        store=True
    )

    @api.multi
    @api.depends('schedule_ids')
    def _compute_count_schedules(self):
        for r in self:
            r.count_schedules = len(r.schedule_ids)
