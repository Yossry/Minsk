# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentTypeDuplicate(models.TransientModel):
    _description = 'Document Type Duplicate'
    _name = 'clv.document.type.duplicate'

    document_type_ids = fields.Many2many(
        comodel_name='clv.document.type',
        relation='clv_document_type_duplicate_rel',
        string='Document Types'
    )

    new_name = fields.Char(
        string='New Document Type',
        required=True
    )

    new_code = fields.Char(
        string='New Document Type Code',
        required=True
    )

    new_description = fields.Char(
        string='New Document Type Description',
        required=False
    )

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        defaults['document_type_ids'] = self.env.context['active_ids']

        DocumentType = self.env['clv.document.type']
        document_type_id = self._context.get('active_id')
        document_type = DocumentType.search([
            ('id', '=', document_type_id),
        ])

        defaults['new_name'] = document_type.name
        defaults['new_code'] = document_type.code
        defaults['new_description'] = document_type.description

        return defaults

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
    def do_document_type_duplicate(self):
        self.ensure_one()

        DocumentType = self.env['clv.document.type']

        document_type_count = 0
        for document_type in self.document_type_ids:

            document_type_count += 1

            _logger.info(u'%s %s %s', '>>>>>', document_type.code, document_type.name)
            _logger.info(u'%s %s %s', '>>>>>>>>>>', self.new_code, self.new_name)

            values = {
                'name': self.new_name,
                'code': self.new_code,
                'description': self.new_description,
            }
            new_document_type = DocumentType.create(values)

        if document_type_count == 1:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Document Types',
                'res_model': 'clv.document.type',
                'res_id': new_document_type.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
                'context': {'search_default_name': new_document_type.name},
            }

        else:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Document Types',
                'res_model': 'clv.document.type',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
            }

        return action
        # return True
