# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcessingSchedule(models.Model):
    _description = 'Processing Schedule'
    _name = 'clv.processing.schedule'
    _order = 'name'

    template_id = fields.Many2one(
        comodel_name='clv.processing.template',
        string='Processing Template',
        required=False,
        ondelete='restrict'
    )

    name = fields.Char(
        string='Name',
        required=True,
        help='Processing Schedule Name'
    )

    external_host_id = fields.Many2one(
        comodel_name='clv.processing.host',
        string='External Host'
    )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    model = fields.Char(
        string='Model',
        required=False,
        help="Model name of the object on which the data processing method to be called is located, e.g. 'res.partner'"
    )

    method = fields.Char(
        string='Method',
        required=False,
        help="Name of the method to be called when the data processing job is processed."
    )

    processing_log = fields.Text(
        string="Processing Log"
    )

    active = fields.Boolean(string='Active', default=1)

    # _sql_constraints = [
    #     ('name_uniq',
    #      'UNIQUE (name)',
    #      u'Error! The Name must be unique!'),
    # ]

    @api.model
    def create(self, values):

        schedule = super().create(values)

        if schedule.template_id.id is not False:
            schedule.external_host_id = schedule.template_id.external_host_id
            schedule.model = schedule.template_id.model
            schedule.method = schedule.template_id.method

        return schedule

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id.id:
            self.external_host_id = self.template_id.external_host_id
            self.model = self.template_id.model
            self.method = self.template_id.method


class ProcessingTemplate(models.Model):
    _inherit = 'clv.processing.template'

    schedule_ids = fields.One2many(
        comodel_name='clv.processing.schedule',
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
