# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PersonAux(models.Model):
    _inherit = 'clv.person_aux'

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
        relation='clv_person_aux_verification_marker_rel',
        column1='person_aux_id',
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
    def person_aux_verification_exec(self):

        VerificationTemplate = self.env['clv.verification.template']
        VerificationOutcome = self.env['clv.verification.outcome']

        model_name = 'clv.person_aux'

        for person_aux in self:

            _logger.info(u'%s %s', '>>>>> (person_aux):', person_aux.name)

            verification_templates = VerificationTemplate.with_context({'active_test': False}).search([
                ('model', '=', model_name),
            ])

            for verification_template in verification_templates:

                _logger.info(u'%s %s', '>>>>>>>>>> (verification_template):', verification_template.name)

                verification_outcome = VerificationOutcome.with_context({'active_test': False}).search([
                    ('model', '=', model_name),
                    ('res_id', '=', person_aux.id),
                    ('action', '=', verification_template.action),
                ])

                if verification_outcome.state is False:

                    verification_outcome_values = {}
                    verification_outcome_values['model'] = model_name
                    verification_outcome_values['res_id'] = person_aux.id
                    verification_outcome_values['res_last_update'] = person_aux['__last_update']
                    verification_outcome_values['state'] = 'Unknown'
                    # verification_outcome_values['method'] = verification_template.method
                    verification_outcome_values['action'] = verification_template.action
                    _logger.info(u'>>>>>>>>>>>>>>> %s %s',
                                 '(verification_outcome_values):', verification_outcome_values)
                    verification_outcome = VerificationOutcome.create(verification_outcome_values)

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (verification_outcome):', verification_outcome)

                action_call = 'self.env["clv.verification.outcome"].' + \
                    verification_outcome.action + \
                    '(verification_outcome, person_aux)'

                _logger.info(u'%s %s', '>>>>>>>>>> (action_call):', action_call)

                if action_call:

                    verification_outcome.state = 'Unknown'
                    verification_outcome.outcome_text = False

                    exec(action_call)

            self.env.cr.commit()

            this_person_aux = self.env['clv.person_aux'].with_context({'active_test': False}).search([
                ('id', '=', person_aux.id),
            ])
            VerificationOutcome._object_verification_outcome_model_object_verification_state_updt(this_person_aux)


class VerificationOutcome(models.Model):
    _inherit = 'clv.verification.outcome'

    def _person_aux_verification(self, verification_outcome, model_object):

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
            # state = 'Error (L0)'

        else:

            if model_object.code is False:

                outcome_info += _('"Person Code" is missing.\n')
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

        if model_object.reg_state not in ['ready', 'done', 'canceled']:

            if model_object.gender is False:

                outcome_info += _('"Gender" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

            if model_object.birthday is False:

                outcome_info += _('"Date of Birth" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

            if (model_object.force_is_deceased is True) and (model_object.date_death is False):

                outcome_info += _('"Deceased Date" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

        if model_object.reg_state not in ['verified', 'ready', 'done', 'canceled']:

            if model_object.phase_id.id is False:

                outcome_info += _('"Phase" is missing.\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

        if (model_object.is_absent is True) and (model_object.state not in ['unavailable']):

                outcome_info += _('"Person (Aux) State" should be "Unavailable".\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

        if (model_object.is_deceased is True) and (model_object.state not in ['unavailable']):

                outcome_info += _('"Person (Aux) State" should be "Unavailable".\n')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

    def _person_aux_verification_related_person(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        related_person = model_object.related_person_id

        state = 'Ok'
        outcome_info = ''

        if model_object.related_person_is_unavailable:

            # if related_person.id is not False:

            #     outcome_info = _('"Related Person" should not be set\n.')
            #     state = 'Error (L0)'

            outcome_info = _('"Related Person is Unavailable" should not be set.\n')
            state = self._get_verification_outcome_state(state, 'Error (L1)')

        else:

            if related_person.id is not False:

                if (model_object.name != related_person.name):

                    outcome_info += _('"Name" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.code != related_person.code):

                    outcome_info += _('"Person Code" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.is_absent != related_person.is_absent):

                    outcome_info += _('"Is Absent" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.gender != related_person.gender):

                    outcome_info += _('"Gender" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.birthday != related_person.birthday):

                    outcome_info += _('"Date of Birth" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.force_is_deceased != related_person.force_is_deceased):

                    outcome_info += _('"Force Is Deceased" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.date_death != related_person.date_death):

                    outcome_info += _('"Deceased Date" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.phase_id != related_person.phase_id):

                    outcome_info += _('"Phase" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.state != related_person.state):

                    outcome_info += _('"State" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.zip != related_person.zip) or \
                   (model_object.street != related_person.street) or \
                   (model_object.street_number != related_person.street_number) or \
                   (model_object.street2 != related_person.street2) or \
                   (model_object.district != related_person.district) or \
                   (model_object.country_id != related_person.country_id) or \
                   (model_object.state_id != related_person.state_id) or \
                   (model_object.city_id != related_person.city_id):

                    outcome_info += _('"Contact Information (Address)" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if ((model_object.phone is not False) and (model_object.phone != related_person.phone)) or \
                   ((model_object.mobile is not False) and (model_object.mobile != related_person.mobile)) or \
                   ((model_object.email is not False) and (model_object.email != related_person.email)):

                    outcome_info += _('"Contact Information (Phones)" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.global_tag_ids.id is not False):

                    related_person_global_tag_ids = []
                    for global_tag_id in related_person.global_tag_ids:
                        related_person_global_tag_ids.append(global_tag_id.id)

                    count_new_global_tag_ids = 0
                    for global_tag_id in model_object.global_tag_ids:
                        if global_tag_id.id not in related_person_global_tag_ids:
                            count_new_global_tag_ids += 1

                    if count_new_global_tag_ids > 0:
                        outcome_info += _('Added "Global Tag(s)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.category_ids.id is not False):

                    related_person_global_tag_ids = []
                    for global_tag_id in related_person.global_tag_ids:
                        related_person_global_tag_ids.append(global_tag_id.id)

                    count_new_global_tag_ids = 0
                    for global_tag_id in model_object.global_tag_ids:
                        if global_tag_id.id not in related_person_global_tag_ids:
                            count_new_global_tag_ids += 1

                    if count_new_global_tag_ids > 0:
                        outcome_info += _('Added "Person Category(ies)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.marker_ids.id is not False):

                    related_person_marker_ids = []
                    for marker_id in related_person.marker_ids:
                        related_person_marker_ids.append(marker_id.id)

                    count_new_marker_ids = 0
                    for marker_id in model_object.marker_ids:
                        if marker_id.id not in related_person_marker_ids:
                            count_new_marker_ids += 1

                    if count_new_marker_ids > 0:
                        outcome_info += _('Added "Person Marker(s)".\n')
                        state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.ref_address_id != related_person.ref_address_id):

                    outcome_info += _('"Address" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if (model_object.family_id != related_person.family_id):

                    outcome_info += _('"Family" has changed.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if model_object.related_person_id.verification_state != 'Ok':

                    outcome_info += _('Related Person "Verification State" is "') + \
                        model_object.related_person_id.verification_state + '".\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Related Person".\n')
                state = self._get_verification_outcome_state(state, 'Error (L1)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

    def _person_aux_verification_ref_address_aux(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        ref_address_aux = model_object.ref_address_aux_id

        state = 'Ok'
        outcome_info = ''

        if model_object.ref_address_aux_is_unavailable:

            if ref_address_aux.id is not False:

                outcome_info = _('"Address (Aux)" should not be set\n.')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            # outcome_info = _('"Address (Aux) is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if ref_address_aux.id is not False:

                if (model_object.zip != ref_address_aux.zip) or \
                   (model_object.street != ref_address_aux.street) or \
                   (model_object.street_number != ref_address_aux.street_number) or \
                   (model_object.street2 != ref_address_aux.street2) or \
                   (model_object.district != ref_address_aux.district) or \
                   (model_object.country_id != ref_address_aux.country_id) or \
                   (model_object.state_id != ref_address_aux.state_id) or \
                   (model_object.city_id != ref_address_aux.city_id):

                    outcome_info += _('Address (Aux) "Contact Information (Address)" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if model_object.ref_address_aux_id.verification_state != 'Ok':

                    outcome_info += _('Address (Aux) "Verification State" is "') + \
                        model_object.ref_address_aux_id.verification_state + '".\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Address (Aux)".\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

    def _person_aux_verification_ref_address(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        ref_address = model_object.ref_address_id

        state = 'Ok'
        outcome_info = ''

        if model_object.ref_address_is_unavailable:

            if ref_address.id is not False:

                outcome_info = _('"Address" should not be set\n.')
                state = self._get_verification_outcome_state(state, 'Error (L1)')

            # outcome_info = _('"Address is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L1)')

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

                    outcome_info += _('Address "Contact Information (Address)" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                if model_object.ref_address_id.verification_state != 'Ok':

                    outcome_info += _('Address "Verification State" is "') + \
                        model_object.ref_address_id.verification_state + '".\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Address".\n')
                state = self._get_verification_outcome_state(state, 'Error (L1)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

    def _person_aux_verification_family_aux(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        family_aux = model_object.family_aux_id

        state = 'Ok'
        outcome_info = ''

        if model_object.family_aux_is_unavailable:

            if family_aux.id is not False:

                outcome_info = _('"Family (Aux)" should not be set\n.')
                state = self._get_verification_outcome_state(state, 'Error (L0)')

            # outcome_info = _('"Family (Aux) is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L0)')

        else:

            if family_aux.id is not False:

                if (model_object.zip != family_aux.zip) or \
                   (model_object.street != family_aux.street) or \
                   (model_object.street_number != family_aux.street_number) or \
                   (model_object.street2 != family_aux.street2) or \
                   (model_object.district != family_aux.district) or \
                   (model_object.country_id != family_aux.country_id) or \
                   (model_object.state_id != family_aux.state_id) or \
                   (model_object.city_id != family_aux.city_id):

                    outcome_info += _('Family (Aux) "Contact Information (Address)" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L0)')

                if model_object.family_aux_id.verification_state != 'Ok':

                    outcome_info += _('Family (Aux) "Verification State" is "') + \
                        model_object.family_aux_id.verification_state + '".\n'
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Family (Aux)".\n')
                state = self._get_verification_outcome_state(state, 'Warning (L0)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )

    def _person_aux_verification_family(self, verification_outcome, model_object):

        _logger.info(u'%s %s', '>>>>>>>>>>>>>>> (model_object):', model_object.name)

        date_verification = datetime.now()

        family = model_object.family_id

        state = 'Ok'
        outcome_info = ''

        if model_object.family_is_unavailable:

            if family.id is not False:

                outcome_info = _('"Family" should not be set\n.')
                state = self._get_verification_outcome_state(state, 'Error (L1)')

            # outcome_info = _('"Family is Unavailable" should not be set.\n')
            # state = self._get_verification_outcome_state(state, 'Error (L1)')

        else:

            if family.id is not False:

                if (model_object.zip != family.zip) or \
                   (model_object.street != family.street) or \
                   (model_object.street_number != family.street_number) or \
                   (model_object.street2 != family.street2) or \
                   (model_object.district != family.district) or \
                   (model_object.country_id != family.country_id) or \
                   (model_object.state_id != family.state_id) or \
                   (model_object.city_id != family.city_id):

                    outcome_info += _('Family "Contact Information (Address)" mismatch.\n')
                    state = self._get_verification_outcome_state(state, 'Warning (L1)')

                # if model_object.family_id.verification_state != 'Ok':

                #     outcome_info += _('Family "Verification State" is "') + \
                #         model_object.family_id.verification_state + '".\n'
                #     state = self._get_verification_outcome_state(state, 'Warning (L1)')

            else:

                outcome_info = _('Missing "Family".\n')
                state = self._get_verification_outcome_state(state, 'Warning (L1)')

        if outcome_info == '':
            outcome_info = False

        self._object_verification_outcome_updt(
            verification_outcome, state, outcome_info, date_verification, model_object
        )
