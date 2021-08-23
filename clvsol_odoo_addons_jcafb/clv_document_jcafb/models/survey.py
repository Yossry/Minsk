# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug import urls

from odoo import api, fields, models
from openerp.exceptions import UserError
from odoo.addons.http_routing.models.ir_http import slug


class Document(models.Model):
    _inherit = 'clv.document'

    survey_id = fields.Many2one(
        comodel_name='survey.survey',
        string='Survey Type')
    survey_user_input_id = fields.Many2one(
        comodel_name='survey.user_input',
        string='Survey User Input'
    )
    base_survey_user_input_id = fields.Many2one(
        comodel_name='survey.user_input',
        string='Base Survey User Input'
    )


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    document_code = fields.Char(
        string='Document Code',
        readonly=True
    )

    person_code = fields.Char(
        string='Person Code',
        readonly=True
    )

    family_code = fields.Char(
        string='Family Code',
        readonly=True
    )

    address_code = fields.Char(
        string='Address Code',
        readonly=True
    )

    document_id = fields.Many2one(
        comodel_name='clv.document',
        string='Related Document'
    )

    notes = fields.Text(string='Notes')

    survey_url = fields.Char(
        string='Survey URL',
        compute="_compute_survey_url"
    )

    def _compute_survey_url(self):

        base_url = '/' if self.env.context.get('relative_url') else \
                   self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for user_input in self:
            user_input.survey_url = \
                urls.url_join(base_url, "survey/fill/%s/%s" % (slug(user_input.survey_id), user_input.token))


class SurveyUserInput_2(models.Model):
    _inherit = 'survey.user_input'

    state_2 = fields.Selection(
        [('new', 'New'),
         ('returned', 'Returned'),
         ('checked', 'Checked'),
         ('validated', 'Validated'),
         ('discarded', 'Discarded'),
         ], string='State 2', default='new', readonly=True, required=True
    )

    @api.model
    def is_allowed_transition(self, old_state_2, new_state_2):
        return True

    @api.multi
    def change_state_2(self, new_state_2):
        for mfile in self:
            if mfile.is_allowed_transition(mfile.state_2, new_state_2):
                mfile.state_2 = new_state_2
            else:
                raise UserError('Status transition (' + mfile.state_2 + ', ' + new_state_2 + ') is not allowed!')

    @api.multi
    def action_new(self):
        for mfile in self:
            mfile.change_state_2('new')

    @api.multi
    def action_returned(self):
        for mfile in self:
            mfile.change_state_2('returned')

    @api.multi
    def action_checked(self):
        for mfile in self:
            mfile.change_state_2('checked')

    @api.multi
    def action_validated(self):
        for mfile in self:
            mfile.change_state_2('validated')

    @api.multi
    def action_discarded(self):
        for mfile in self:
            mfile.change_state_2('discarded')
