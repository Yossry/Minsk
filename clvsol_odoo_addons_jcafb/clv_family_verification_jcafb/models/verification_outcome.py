# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Family(models.Model):
    _inherit = 'clv.family'

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
        relation='clv_family_verification_marker_rel',
        column1='family_id',
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
    def family_verification_exec(self):

        VerificationTemplate = self.env['clv.verification.template']
        VerificationOutcome = self.env['clv.verification.outcome']

        model_name = 'clv.family'

        for family in self:

            _logger.info(u'%s %s', '>>>>> (family):', family.name)

            verification_templates = VerificationTemplate.with_context({'active_test': False}).search([
                ('model', '=', model_name),
            ])

            for verification_template in verification_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (verification_template):', verification_template.name)

                verification_outcome = VerificationOutcome.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', family.id),
                    ('action', '=', verification_template.action),
                ])

                if verification_outcome.state is False:

                    verification_outcome_values = {}
                    verification_outcome_values['model'] = model_name
                    verification_outcome_values['res_id'] = family.id
                    verification_outcome_values['res_last_update'] = family['__last_update']
                    verification_outcome_values['state'] = 'Unknown'
                    # verification_outcome_values['method'] = verification_template.method
                    verification_outcome_values['action'] = verification_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(verification_outcome_values):', verification_outcome_values)
                    verification_outcome = VerificationOutcome.create(verification_outcome_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (verification_outcome):', verification_outcome)

                action_call = 'self.env["clv.verification.outcome"].' + \
                    verification_outcome.action + \
                    '(verification_outcome, family)'

                _logger.info(u'%s %s', '>>>>>>>>>>', action_call)

                if action_call:

                    verification_outcome.state = 'Unknown'
                    verification_outcome.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            this_family = self.env['clv.family'].with_context({'active_test': False}).search([
                ('id', '=', family.id),
            ])
            VerificationOutcome._object_verification_outcome_model_object_verification_state_updt(this_family)


class VerificationOutcome(models.Model):
    _inherit = 'clv.verification.outcome'

    def _family_verification(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        PartnerEntityStreetPattern = self.env['clv.partner_entity.street_pattern']

        state = 'Ok'
        outcome_info = ''

        if model_object.contact_info_is_unavailable:

            if model_object.street is not False:

                outcome_info = _('"Contact Information" should not be set.\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            # outcome_info = _('"Contact Information is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if model_object.street is False:

                outcome_info += _('"Contact Information" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            if model_object.reg_state not in ['done', 'canceled']:

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

    def _family_verification_ref_address(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        ref_address = model_object.ref_address_id

        state = 'Ok'
        outcome_info = ''

        if model_object.ref_address_is_unavailable:

            if ref_address.id is not False:

                outcome_info = _('"Address" should not be set\n.')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            # outcome_info = _('"Address is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if ref_address.id is not False:

                if (model_object.zip != ref_address.zip) or \
                   (model_object.street != ref_address.street) or \
                   (model_object.street_number != ref_address.street_number) or \
                   (model_object.street2 != ref_address.street2) or \
                   (model_object.district != ref_address.district) or \
                   (model_object.country_id != ref_address.country_id) or \
                   (model_object.state_id != ref_address.state_id) or \
                   (model_object.city_id != ref_address.city_id):

                    outcome_info += _('Address "Contact Information" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                Family = self.env['clv.family']

                ref_address_families = Family.search([
                    ('ref_address_id', '=', ref_address.id),
                ])

                for ref_address_familiy in ref_address_families:

                    if ref_address_familiy.id != model_object.id:

                        outcome_info += _('Additional Family at the same Address.') + \
                            ' (' + ref_address_familiy.name + ' [' + ref_address_familiy.code + '])\n'
                        state = self._get_verification_outcome_state(state, 'Error (L0)')

                if ref_address.state != model_object.state:

                    outcome_info += _('Address "State" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if ref_address.phase_id.id != model_object.phase_id.id:

                    outcome_info += _('Address "Phase" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

            else:

                outcome_info = _('Missing "Address".')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

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

    def _family_verification_associated_persons(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        state = 'Ok'
        outcome_info = ''

        Person = self.env['clv.person']

        family_associated_persons = Person.search([
            ('family_id', '=', model_object.id),
        ])

        associated_person_list = []

        for family_associated_person in family_associated_persons:

            associated_person_list.append(family_associated_person.id)

            if model_object.ref_address_id.id != family_associated_person.ref_address_id.id:

                outcome_info += _('Associated Person "Address" mismatch.') + \
                    ' (' + family_associated_person.name + ' [' + family_associated_person.code + '])\n'
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

        if model_object.ref_address_id.id is not False:

            ref_address_associated_persons = Person.search([
                ('ref_address_id', '=', model_object.ref_address_id.id),
            ])

            for ref_address_associated_person in ref_address_associated_persons:

                if (ref_address_associated_person.id not in associated_person_list) and \
                   (ref_address_associated_person.family_id.id is False):

                    outcome_info += _('Missing Associated Person.') + \
                        ' (' + ref_address_associated_person.name + ' [' + ref_address_associated_person.code + '])\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

        verification_values = {}
        verification_values['date_verification'] = date_verification
        verification_values['outcome_info'] = outcome_info
        verification_values['state'] = state
        verification_outcome.write(verification_values)
