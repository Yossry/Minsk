# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from functools import reduce
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class VerificationOutcome(models.Model):
    _description = 'Verification Outcome'
    _name = 'clv.verification.outcome'
    _order = "id desc"
    _rec_name = 'reference_name'

    date_verification = fields.Datetime(string="Verification Date")
    state = fields.Selection(
        [('Error (L0)', 'Error (L0)'),
         ('Warning (L0)', 'Warning (L0)'),
         ('Error (L1)', 'Error (L1)'),
         ('Warning (L1)', 'Warning (L1)'),
         ('Error (L2)', 'Error (L2)'),
         ('Warning (L2)', 'Warning (L2)'),
         ('Ok', 'Ok'),
         ('Updated', 'Updated'),
         ('Unknown', 'Unknown'),
         ('Missing', 'Missing'),
         ], string='State', default='Unknown'
    )
    outcome_info = fields.Text(string='Outcome Informations')

    model = fields.Char(string='Model Name ', required=True)
    res_id = fields.Integer(
        string='Record ID',
        help="ID of the target record in the database",
        required=True
    )
    res_last_update = fields.Datetime(string="Record Last Update")
    reference = fields.Char(
        string='Reference ',
        compute='_compute_reference',
        readonly=True,
        store=True
    )
    reference_name = fields.Char(
        string='Reference Name',
        compute='_compute_reference',
        readonly=True,
        store=True
    )

    # method = fields.Char(
    #     string='Method',
    #     required=False,
    #     help="Name of the method to be called when the verification job is processed."
    # )

    action = fields.Char(
        string='Action',
        required=False,
        help="Name of the action used to process the verification."
    )

    active = fields.Boolean(string='Active', default=1)

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for record in self:
            if (record.model is not False) and (record.res_id != 0):
                record.reference = "%s,%s" % (record.model, record.res_id)
                Model = self.env[record.model]
                rec = Model.search([
                    ('id', '=', record.res_id),
                ])
                record.reference_name = rec.name_get()[0][1]

    # def _object_verify(self, schedule):

    #     model_name = schedule.model

    #     verification_outcome = self

    #     ModelObject = self.env[model_name]
    #     model_object = ModelObject.with_context({'active_test': False}).search([
    #         ('id', '=', self.res_id),
    #     ])

    #     _logger.info(u'%s %s', '>>>>>>>>>> (verification_outcome):', verification_outcome)

    #     _logger.info(u'%s %s', '>>>>>>>>>> (model_object):', model_object)

    #     action_call = 'self.env["clv.verification.outcome"].' + \
    #         schedule.action + \
    #         '(verification_outcome, model_object)'

    #     _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

    #     if action_call:

    #         self.method = schedule.method
    #         self.action = schedule.action
    #         self.state = 'Unknown'
    #         self.outcome_info = False

    #         exec(action_call)

    # def _object_verification(self, schedule):

    #     if (not schedule.verification_disable_identification) or (not schedule.verification_disable_check_missing):
    #         self._object_verification_identify(schedule)

    #     from time import time
    #     start = time()

    #     if (not schedule.verification_disable_inclusion) or \
    #        (not schedule.verification_disable_verification):

    #         VerificationOutcome = self.env['clv.verification.outcome']

    #         model_name = schedule.model

    #         verification_max_task = schedule.verification_max_task

    #         date_last_sync = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         upmost_last_update = False

    #         schedule.verification_log += 'Executing: "' + '_object_verification' + '"...\n\n'

    #         verification_outcome_objects = VerificationOutcome.with_context({'active_test': False}).search([
    #             ('model', '=', model_name),
    #             ('action', '=', schedule.action),
    #             ('state', '!=', 'Missing'),
    #             ('state', '!=', 'Ok'),
    #         ])
    #         _logger.info(u'%s %s', '>>>>>>>>>> (verification_outcome_objects):', len(verification_outcome_objects))

    #         reg_count = 0
    #         include_count = 0
    #         update_count = 0
    #         verification_count = 0
    #         verification_include_count = 0
    #         verification_update_count = 0
    #         task_count = 0
    #         for verification_object in verification_outcome_objects:

    #             reg_count += 1

    #             _logger.info(u'%s %s %s %s', '>>>>>>>>>>', reg_count,
    #                          verification_object.res_id,
    #                          verification_object.res_last_update, )

    #             if task_count >= verification_max_task:
    #                 continue

    #             if upmost_last_update is False:
    #                 upmost_last_update = verification_object.res_last_update
    #             else:
    #                 if verification_object.res_last_update is not False:
    #                     if verification_object.res_last_update > upmost_last_update:
    #                         upmost_last_update = verification_object.res_last_update

    #             if verification_object.res_id == 0:

    #                 include_count += 1
    #                 task_count += 1

    #                 verification_object._object_verify(schedule)

    #                 self.env.cr.commit()

    #             else:

    #                 if verification_object.date_verification is False or \
    #                    ((verification_object.date_verification >
    #                      verification_object.res_last_update) and
    #                         verification_object.state != 'Unknown'):

    #                     update_count += 1
    #                     task_count += 1

    #                     verification_object.state = 'Updated'

    #                 if (verification_object.state == 'Unknown' or
    #                     verification_object.state == 'Updated') and \
    #                    schedule.verification_disable_verification is False:

    #                     verification_count += 1
    #                     task_count += 1

    #                     _logger.info(u'>>>>>>>>>>>>>>> %s %s', verification_count, verification_object)

    #                     if verification_object.state == 'Unknown':
    #                         verification_include_count += 1

    #                     if verification_object.state == 'Updated':
    #                         verification_update_count += 1

    #                     verification_object._object_verify(schedule)

    #                 self.env.cr.commit()

    #         _logger.info(u'%s %s', '>>>>>>>>>> verification_max_task: ', verification_max_task)
    #         _logger.info(u'%s %s', '>>>>>>>>>> verification_outcome_objects: ', len(verification_outcome_objects))
    #         _logger.info(u'%s %s', '>>>>>>>>>> reg_count: ', reg_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> include_count: ', include_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> update_count: ', update_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> verification_include_count: ', verification_include_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> verification_update_count: ', verification_update_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> verification_count: ', verification_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> task_count: ', task_count)
    #         _logger.info(u'%s %s', '>>>>>>>>>> date_last_sync: ', date_last_sync)
    #         _logger.info(u'%s %s', '>>>>>>>>>> upmost_last_update: ', upmost_last_update)
    #         _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))

    #         schedule.date_last_sync = date_last_sync
    #         schedule.upmost_last_update = upmost_last_update
    #         schedule.verification_log +=  \
    #             'verification_outcome_objects: ' + str(len(verification_outcome_objects)) + '\n' + \
    #             'reg_count: ' + str(reg_count) + '\n' + \
    #             'include_count: ' + str(include_count) + '\n' + \
    #             'update_count: ' + str(update_count) + '\n' + \
    #             'verification_include_count: ' + str(verification_include_count) + '\n' + \
    #             'verification_update_count: ' + str(verification_update_count) + '\n' + \
    #             'verification_count: ' + str(verification_count) + '\n\n' + \
    #             'task_count: ' + str(task_count) + '\n\n' + \
    #             'date_last_sync: ' + str(date_last_sync) + '\n' + \
    #             'upmost_last_update: ' + str(upmost_last_update) + '\n\n' + \
    #             'Execution time: ' + str(secondsToStr(time() - start)) + '\n'

    # def _object_verification_identify(self, schedule):

    #     from time import time
    #     start = time()

    #     model_name = schedule.model

    #     ModelObject = self.env[model_name]
    #     VerificationOutcome = self.env['clv.verification.outcome']

    #     verification_disable_identification = schedule.verification_disable_identification
    #     verification_disable_check_missing = schedule.verification_disable_check_missing

    #     verification_max_task = schedule.verification_max_task
    #     upmost_last_update = False
    #     date_last_sync = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #     schedule.verification_log += 'Executing: "' + '_object_verification_identify' + '"...\n\n'

    #     verification_object_ids = []
    #     verification_outcomes = []
    #     missing_count = 0
    #     reg_count_2 = 0
    #     if not verification_disable_check_missing:

    #         verification_object_ids = []
    #         model_objects = ModelObject.with_context({'active_test': False}).search([])
    #         for model_object in model_objects:
    #             verification_object_ids.append(model_object.id)
    #         _logger.info(u'%s %s', '>>>>>>>>>> (verification_outcome_objects):', len(verification_object_ids))

    #         verification_outcomes = VerificationOutcome.with_context({'active_test': False}).search([
    #             ('model', '=', model_name),
    #             ('res_id', '!=', False),
    #             ('action', '=', schedule.action),
    #             ('state', '!=', 'Missing'),
    #         ])
    #         _logger.info(u'%s %s', '>>>>>>>>>> (verification_outcomes):', len(verification_outcomes))

    #         for verification_outcome in verification_outcomes:
    #             _logger.info(u'%s %s %s', '>>>>>>>>>>', reg_count_2, verification_outcome, )
    #             if verification_outcome.res_id not in verification_object_ids:
    #                 missing_count += 1
    #                 _logger.info(u'%s %s %s', '>>>>>>>>>>>>>>> (missing_object):',
    #                              missing_count, verification_outcome.id)
    #                 verification_outcome.outcome_info = \
    #                     verification_outcome.model + ' (' + str(verification_outcome.res_id) + ') - ' + \
    #                     verification_outcome.reference_name
    #                 verification_outcome.res_id = 0
    #                 verification_outcome.state = 'Missing'
    #             reg_count_2 += 1
    #             self.env.cr.commit()

    #     verification_args = schedule.verification_last_update_args()
    #     verification_outcome_objects = []
    #     reg_count = 0
    #     include_count = 0
    #     update_count = 0
    #     task_count = 0
    #     if not verification_disable_identification:

    #         verification_args = schedule.verification_last_update_args()
    #         _logger.info(u'%s %s', '>>>>>>>>>> (verification_args):', verification_args)

    #         verification_outcome_objects = ModelObject.with_context({'active_test': False}).search(
    #             verification_args
    #         )

    #         _logger.info(u'%s %s', '>>>>>>>>>> (verification_outcome_objects):', len(verification_outcome_objects))

    #         for verification_object in verification_outcome_objects:

    #             reg_count += 1

    #             _logger.info(u'%s %s %s %s', '>>>>>>>>>>', reg_count,
    #                          verification_object['id'],
    #                          verification_object['__last_update'], )

    #             if task_count >= verification_max_task:
    #                 continue

    #             if upmost_last_update is False:
    #                 upmost_last_update = verification_object['__last_update']
    #             else:
    #                 if verification_object['__last_update'] > upmost_last_update:
    #                     upmost_last_update = verification_object['__last_update']

    #             verification_outcome = VerificationOutcome.with_context({'active_test': False}).search([
    #                 ('model', '=', model_name),
    #                 ('res_id', '=', verification_object['id']),
    #                 ('action', '=', schedule.action),
    #             ])

    #             if verification_outcome.id is False:

    #                 task_count += 1

    #                 include_count += 1

    #                 verification_outcome_values = {}
    #                 verification_outcome_values['model'] = model_name
    #                 verification_outcome_values['res_id'] = verification_object['id']
    #                 verification_outcome_values['res_last_update'] = verification_object['__last_update']
    #                 verification_outcome_values['action'] = schedule.action
    #                 verification_outcome_values['state'] = 'Unknown'
    #                 _logger.info(u'>>>>>>>>>>>>>>> %s %s', include_count, verification_outcome_values)
    #                 VerificationOutcome.create(verification_outcome_values)

    #                 self.env.cr.commit()

    #             else:

    #                 if verification_outcome.res_last_update is not False:
    #                     if verification_object['__last_update'] > verification_outcome.res_last_update:

    #                         task_count += 1
    #                         update_count += 1

    #                         verification_outcome.res_last_update = verification_object['__last_update']

    #                         if verification_outcome.state == 'Ok':
    #                             verification_outcome.state = 'Updated'

    #                         _logger.info(u'>>>>>>>>>>>>>>> %s %s', update_count, verification_outcome)

    #                         self.env.cr.commit()

    #     _logger.info(u'%s %s', '>>>>>>>>>> verification_max_task: ', verification_max_task)
    #     _logger.info(u'%s %s', '>>>>>>>>>> verification_args: ', verification_args)
    #     _logger.info(u'%s %s', '>>>>>>>>>> verification_object_ids: ', len(verification_object_ids))
    #     _logger.info(u'%s %s', '>>>>>>>>>> verification_outcomes: ', len(verification_outcomes))
    #     _logger.info(u'%s %s', '>>>>>>>>>> reg_count_2: ', reg_count_2)
    #     _logger.info(u'%s %s', '>>>>>>>>>> missing_count: ', missing_count)
    #     _logger.info(u'%s %s', '>>>>>>>>>> reg_count: ', reg_count)
    #     _logger.info(u'%s %s', '>>>>>>>>>> include_count: ', include_count)
    #     _logger.info(u'%s %s', '>>>>>>>>>> update_count: ', update_count)
    #     _logger.info(u'%s %s', '>>>>>>>>>> task_count: ', task_count)
    #     _logger.info(u'%s %s', '>>>>>>>>>> date_last_sync: ', date_last_sync)
    #     _logger.info(u'%s %s', '>>>>>>>>>> upmost_last_update: ', upmost_last_update)
    #     _logger.info(u'%s %s', '>>>>>>>>>> Execution time: ', secondsToStr(time() - start))

    #     schedule.date_last_sync = date_last_sync
    #     schedule.upmost_last_update = upmost_last_update
    #     schedule.verification_log +=  \
    #         'verification_args: ' + str(verification_args) + '\n\n' + \
    #         'verification_object_ids: ' + str(len(verification_object_ids)) + '\n' + \
    #         'verification_outcomes: ' + str(len(verification_outcomes)) + '\n' + \
    #         'reg_count_2: ' + str(reg_count_2) + '\n' + \
    #         'missing_count: ' + str(missing_count) + '\n\n' + \
    #         'verification_outcome_objects: ' + str(len(verification_outcome_objects)) + '\n' + \
    #         'reg_count: ' + str(reg_count) + '\n' + \
    #         'include_count: ' + str(include_count) + '\n' + \
    #         'update_count: ' + str(update_count) + '\n' + \
    #         'task_count: ' + str(task_count) + '\n\n' + \
    #         'date_last_sync: ' + str(date_last_sync) + '\n' + \
    #         'upmost_last_update: ' + str(upmost_last_update) + '\n\n' + \
    #         'Execution time: ' + str(secondsToStr(time() - start)) + '\n\n'

    def _get_verification_outcome_state(self, current_state, new_state):

        verification_state = current_state

        if new_state == 'Error (L0)':
            verification_state = 'Error (L0)'
        elif (new_state == 'Warning (L0)') and \
             (current_state not in ['Error (L0)']):
            verification_state = 'Warning (L0)'
        elif (new_state == 'Error (L1)') and \
             (current_state not in ['Warning (L0)', 'Error (L0)']):
            verification_state = 'Error (L1)'
        elif (new_state == 'Warning (L1)') and \
             (current_state not in ['Error (L1)', 'Warning (L0)', 'Error (L0)']):
            verification_state = 'Warning (L1)'
        elif (new_state == 'Error (L2)') and \
             (current_state not in ['Warning (L1)', 'Error (L1)', 'Warning (L0)', 'Error (L0)']):
            verification_state = 'Error (L2)'
        elif (new_state == 'Warning (L2)') and \
             (current_state not in ['Error (L2)', 'Warning (L1)', 'Error (L1)', 'Warning (L0)', 'Error (L0)']):
            verification_state = 'Warning (L2)'
        elif (new_state == 'Ok') and \
             (current_state not in ['Warning (L2)', 'Error (L2)', 'Warning (L1)', 'Error (L1)',
                                    'Warning (L0)', 'Error (L0)']):
            verification_state = 'Ok'
        elif (new_state not in ['Ok', 'Warning (L2)', 'Error (L2)', 'Warning (L1)', 'Error (L1)',
                                'Warning (L0)', 'Error (L0)']):
            verification_state = new_state

        return verification_state

    def _object_verification_outcome_model_object_verification_state_updt(self, model_object):

        _logger.info(u'%s %s -> %s', '>>>>>>>>>>>>>>>>>>>>',
                     model_object, model_object.verification_outcome_ids)

        verification_state = 'Unknown'
        for verification_outcome in model_object.verification_outcome_ids:
            verification_state = self._get_verification_outcome_state(verification_state,
                                                                      verification_outcome.state)
        if model_object.verification_state != verification_state:
            model_object.verification_state = verification_state

    def _object_verification_outcome_updt(
        self, verification_outcome, state, outcome_info, date_verification, model_object
    ):

        verification_values = {}
        verification_values['date_verification'] = date_verification
        verification_values['outcome_info'] = outcome_info
        verification_values['state'] = state
        verification_outcome.write(verification_values)
