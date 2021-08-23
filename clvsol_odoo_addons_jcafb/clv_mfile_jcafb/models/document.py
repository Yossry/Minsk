# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class MediaFile(models.Model):
    _inherit = 'clv.mfile'

    document_id = fields.Many2one(
        comodel_name='clv.document',
        string='Related Document'
    )
    document_code = fields.Char(
        string='Document Code',
        related='document_id.code',
        store=False,
        readonly=True
    )
    document_type_id = fields.Many2one(
        comodel_name='clv.document.type',
        string='Document Type',
        related='document_id.document_type_id',
        store=True,
        readonly=True
    )
    document_state = fields.Selection(
        string='Document State',
        related='document_id.state',
        store=True,
        readonly=True
    )

    survey_id = fields.Many2one(
        comodel_name='survey.survey',
        string='Survey Type',
        related='document_id.survey_id',
        store=True,
        readonly=True
    )
    survey_description = fields.Html(
        string='Survey Type Description',
        related='document_id.survey_id.description',
        store=False,
        readonly=True
    )
    survey_user_input_id = fields.Many2one(
        comodel_name='survey.user_input',
        string='Survey User Input',
        related='document_id.survey_user_input_id',
        store=False,
        readonly=True
    )

    ref_id = fields.Reference(
        selection='referenceable_models',
        string='Refers to',
        related='document_id.ref_id',
        store=False,
        readonly=True
    )
    ref_model = fields.Char(
        string='Refers to (Model)',
        related='document_id.ref_model',
        store=False,
        readonly=True
    )
    ref_name = fields.Char(
        string='Refers to (Name)',
        related='document_id.ref_name',
        store=False,
        readonly=True
    )
    ref_code = fields.Char(
        string='Refers to (Code)',
        related='document_id.ref_code',
        store=False,
        readonly=True
    )
    # lab_test_request_code = fields.Char(string="Lab Test Request Code")
    # lab_test_request_id = fields.Many2one(
    #     comodel_name='clv.lab_test.request',
    #     string="Related Lab Test Request"
    # )
