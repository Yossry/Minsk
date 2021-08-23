# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AddressAux(models.Model):
    _inherit = 'clv.address_aux'

    verification_outcome_ids = fields.One2many(
        string='Verification Outcomes',
        comodel_name='clv.verification.outcome',
        compute='_compute_verification_outcome_ids_and_count',
    )
    count_verification_outcomes = fields.Integer(
        string='Verification Outcomes (count)',
        compute='_compute_verification_outcome_ids_and_count',
    )
    count_verification_outcomes_2 = fields.Integer(
        string='Verification Outcomes 2 (count)',
        compute='_compute_verification_outcome_ids_and_count',
    )

    verification_state = fields.Char(
        string='Verification State',
        default='Unknown',
        readonly=True
    )

    verification_marker_ids = fields.Many2many(
        comodel_name='clv.verification.marker',
        relation='clv_address_aux_verification_marker_rel',
        column1='address_aux_id',
        column2='verification_marker_id',
        string='Verification Markers'
    )
    verification_marker_names = fields.Char(
        string='Verification Marker Names',
        compute='_compute_verification_marker_names',
        store=True
    )

    @api.multi
    def _compute_verification_outcome_ids_and_count(self):
        for record in self:

            search_domain = [
                ('model', '=', self._name),
                ('res_id', '=', record.id),
            ]

            verification_outcomes = self.env['clv.verification.outcome'].search(search_domain)

            record.count_verification_outcomes = len(verification_outcomes)
            record.count_verification_outcomes_2 = len(verification_outcomes)
            record.verification_outcome_ids = [(6, 0, verification_outcomes.ids)]

    @api.depends('verification_marker_ids')
    def _compute_verification_marker_names(self):
        for r in self:
            verification_marker_names = False
            for verification_marker in r.verification_marker_ids:
                if verification_marker_names is False:
                    verification_marker_names = verification_marker.name
                else:
                    verification_marker_names = verification_marker_names + ', ' + verification_marker.name
            r.verification_marker_names = verification_marker_names

    @api.multi
    def address_aux_verification_exec(self):

        VerificationTemplate = self.env['clv.verification.template']
        VerificationOutcome = self.env['clv.verification.outcome']

        model_name = 'clv.address_aux'

        for address_aux in self:

            _logger.info(u'%s %s', '>>>>> (address_aux):', address_aux.name)

            verification_templates = VerificationTemplate.with_context({'active_test': False}).search([
                ('model', '=', model_name),
            ])

            for verification_template in verification_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (verification_template):', verification_template.name)

                verification_outcome = VerificationOutcome.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', address_aux.id),
                    ('action', '=', verification_template.action),
                ])

                if verification_outcome.state is False:

                    verification_outcome_values = {}
                    verification_outcome_values['model'] = model_name
                    verification_outcome_values['res_id'] = address_aux.id
                    verification_outcome_values['res_last_update'] = address_aux['__last_update']
                    verification_outcome_values['state'] = 'Unknown'
                    # verification_outcome_values['method'] = verification_template.method
                    verification_outcome_values['action'] = verification_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(verification_outcome_values):', verification_outcome_values)
                    verification_outcome = VerificationOutcome.create(verification_outcome_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (verification_outcome):', verification_outcome)

                action_call = 'self.env["clv.verification.outcome"].' + \
                    verification_outcome.action + \
                    '(verification_outcome, address_aux)'

                _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

                if action_call:

                    verification_outcome.state = 'Unknown'
                    verification_outcome.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            this_address_aux = self.env['clv.address_aux'].with_context({'active_test': False}).search([
                ('id', '=', address_aux.id),
            ])
            VerificationOutcome._object_verification_outcome_model_object_verification_state_updt(this_address_aux)


class VerificationOutcome(models.Model):
    _inherit = 'clv.verification.outcome'

    def _address_aux_verification(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        PartnerEntityStreetPattern = self.env['clv.partner_entity.street_pattern']

        state = 'Ok'
        outcome_info = ''

        if model_object.contact_info_is_unavailable:

            # if model_object.street is not False:

            #     outcome_info = _('"Contact Information" should not be set.\n')
            #     state = self._get_verification_outcome_state(state, 'Error (L0)')

            outcome_info = _('"Contact Information is Unavailable" should not be set.\n')
            state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if model_object.code is False:

                outcome_info += _('"Address Code" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

            if model_object.street is False:

                outcome_info += _('"Contact Information" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            if model_object.reg_state not in ['verified', 'ready', 'done', 'canceled']:

                street_patern = PartnerEntityStreetPattern.search([
                    ('street', '=', model_object.street),
                    ('district', '=', model_object.district),
                ])

                if street_patern.street is False:

                    outcome_info += _('"Street Pattern" was not recognised.') + \
                        ' (' + str(model_object.street) + ' [' + str(model_object.district) + '])\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.zip is False) or \
                   (model_object.street is False) or \
                   (model_object.district is False) or \
                   (model_object.country_id is False) or \
                   (model_object.state_id is False) or \
                   (model_object.city_id is False):

                    outcome_info += _('Please, verify "Contact Information (Street)" data.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.zip is False) or \
                   (model_object.street is False) or \
                   (model_object.street_number is False) or \
                   (model_object.street2 is False) or \
                   (model_object.district is False) or \
                   (model_object.country_id is False) or \
                   (model_object.state_id is False) or \
                   (model_object.city_id is False):

                    outcome_info += _('Please, verify "Contact Information (Complement)" data.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

        if model_object.phase_id.id is False:

            outcome_info += _('"Phase" is missing.\n')
            state = self._get_verification_outcome_state(state, 'Error (L0)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

        verification_values = {}
        verification_values['date_verification'] = date_verification
        verification_values['outcome_info'] = outcome_info
        verification_values['state'] = state
        verification_outcome.write(verification_values)

    def _address_aux_verification_related_address(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        related_address = model_object.related_address_id

        state = 'Ok'
        outcome_info = ''

        if model_object.related_address_is_unavailable:

            # if related_address.id is not False:

            #     outcome_info = _('"Related Address" should not be set\n.')
            #     state = self._get_verification_outcome_state(state, 'Error (L0)')

            outcome_info = _('"Related Address is Unavailable" should not be set.\n')
            state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if related_address.id is not False:

                if (model_object.name != related_address.name):

                    outcome_info += _('"Name" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.code != related_address.code):

                    outcome_info += _('"Address Code" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.phase_id != related_address.phase_id):

                    outcome_info += _('"Phase" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                # if (model_object.reg_state != related_address.reg_state):

                #     outcome_info += _('"Register State" has changed.\n')
                #     state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.state != related_address.state):

                    outcome_info += _('"State" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.zip != related_address.zip) or \
                   (model_object.street != related_address.street) or \
                   (model_object.street_number != related_address.street_number) or \
                   (model_object.street2 != related_address.street2) or \
                   (model_object.district != related_address.district) or \
                   (model_object.country_id != related_address.country_id) or \
                   (model_object.state_id != related_address.state_id) or \
                   (model_object.city_id != related_address.city_id):

                    outcome_info += _('"Contact Information (Address)" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if (model_object.phone != related_address.phone) or \
                   (model_object.mobile != related_address.mobile) or \
                   (model_object.email != related_address.email):

                    outcome_info += _('"Contact Information (Phone)" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if model_object.related_address_id.verification_state != 'Ok':

                    outcome_info += _('Related Address "Verification State" is "') + \
                        model_object.related_address_id.verification_state + '".\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.global_tag_ids.id is not False):

                    related_address_global_tag_ids = []
                    for global_tag_id in related_address.global_tag_ids:
                        related_address_global_tag_ids.append(global_tag_id.id)

                    count_new_global_tag_ids = 0
                    for global_tag_id in model_object.global_tag_ids:
                        if global_tag_id.id not in related_address_global_tag_ids:
                            count_new_global_tag_ids += 1

                    if count_new_global_tag_ids > 0:
                        outcome_info += _('Added "Global Tag(s)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.category_ids.id is not False):

                    related_address_global_tag_ids = []
                    for global_tag_id in related_address.global_tag_ids:
                        related_address_global_tag_ids.append(global_tag_id.id)

                    count_new_global_tag_ids = 0
                    for global_tag_id in model_object.global_tag_ids:
                        if global_tag_id.id not in related_address_global_tag_ids:
                            count_new_global_tag_ids += 1

                    if count_new_global_tag_ids > 0:
                        outcome_info += _('Added "Person Category(ies)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.marker_ids.id is not False):

                    related_address_marker_ids = []
                    for marker_id in related_address.marker_ids:
                        related_address_marker_ids.append(marker_id.id)

                    count_new_marker_ids = 0
                    for marker_id in model_object.marker_ids:
                        if marker_id.id not in related_address_marker_ids:
                            count_new_marker_ids += 1

                    if count_new_marker_ids > 0:
                        outcome_info += _('Added "Person Marker(s)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Related Address".\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

        verification_values = {}
        verification_values['date_verification'] = date_verification
        verification_values['outcome_info'] = outcome_info
        verification_values['state'] = state
        verification_outcome.write(verification_values)
