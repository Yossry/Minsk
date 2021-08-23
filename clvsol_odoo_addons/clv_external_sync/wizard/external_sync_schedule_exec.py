# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ExternalSyncScheduleExec(models.TransientModel):
    _description = 'External Sync Schedule Exec'
    _name = 'clv.external_sync.schedule.exec'

    def _default_schedule_ids(self):
        return self._context.get('active_ids')
    schedule_ids = fields.Many2many(
        comodel_name='clv.external_sync.schedule',
        relation='clv_external_sync_schedule_exec_rel',
        string='Schedules to Execute',
        default=_default_schedule_ids)
    count_schedules = fields.Integer(
        string='Number of Schedules',
        compute='_compute_count_schedules',
        store=False
    )

    @api.multi
    @api.depends('schedule_ids')
    def _compute_count_schedules(self):
        for r in self:
            r.count_schedules = len(r.schedule_ids)

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_external_sync_schedule_exec(self):
        self.ensure_one()

        for schedule in self.schedule_ids:

            model = schedule.model
            external_model = schedule.external_model
            _logger.info(u'%s %s [%s - %s]', '>>>>>', schedule.name, model, external_model)

            method_call = False
            if schedule.method == '_object_external_sync':
                method_call = 'self.env["clv.external_sync"].' + schedule.method + '(schedule)'
            elif schedule.method == '_object_external_recognize':
                method_call = 'self.env["clv.external_sync"].' + schedule.method + '(schedule)'

            # if schedule.external_disable_check_missing is not False:
            #     method = '_object_external_identify'
            #     method_call = 'self.env["clv.external_sync"].' + method + '(schedule)'
            # method = '_object_external_identify'
            # method_call = 'self.env["clv.external_sync"].' + method + '(schedule)'

            _logger.info(u'%s %s', '>>>>>>>>>>', method_call)

            if method_call:

                schedule.external_sync_log = 'method: ' + str(schedule.method) + '\n\n'
                schedule.external_sync_log +=  \
                    'external_host: ' + str(schedule.external_host_id.name) + '\n' + \
                    'external_dbname: ' + str(schedule.external_host_id.external_dbname) + '\n\n' + \
                    'external_max_task: ' + str(schedule.external_max_task) + '\n' + \
                    'external_disable_identification: ' + str(schedule.external_disable_identification) + '\n' + \
                    'external_disable_check_missing: ' + str(schedule.external_disable_check_missing) + '\n' + \
                    'external_disable_inclusion: ' + str(schedule.external_disable_inclusion) + '\n' + \
                    'external_disable_sync: ' + str(schedule.external_disable_sync) + '\n' + \
                    'external_last_update_args: ' + str(schedule.external_last_update_args()) + '\n\n' + \
                    'enable_sequence_code_sync: ' + str(schedule.enable_sequence_code_sync) + '\n\n'

                exec(method_call)

        return True
        # return self._reopen_form()
