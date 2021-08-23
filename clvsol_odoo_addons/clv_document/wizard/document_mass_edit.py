# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

'''
Reference: http://help.openerp.com/question/18704/hide-menu-for-existing-group/

There are actually0-6 numbers for representing each job for a many2many/ one2many field

    (0, 0, { values }) -- link to a new record that needs to be created with the given values dictionary
    (1, ID, { values }) -- update the linked record with id = ID (write values on it)
    (2, ID) -- remove and delete the linked record with id = ID (calls unlink on ID, that will delete the
               object completely, and the link to it as well)
    (3, ID) -- cut the link to the linked record with id = ID (delete the relationship between the two
               objects but does not delete the target object itself)
    (4, ID) -- link to existing record with id = ID (adds a relationship)
    (5) -- unlink all (like using (3,ID) for all linked records)
    (6, 0, [IDs]) -- replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)
'''

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocumentMassEdit(models.TransientModel):
    _description = 'Document Mass Edit'
    _name = 'clv.document.mass_edit'

    def _default_document_ids(self):
        return self._context.get('active_ids')
    document_ids = fields.Many2many(
        comodel_name='clv.document',
        relation='clv_document_mass_edit_rel',
        string='Documents',
        default=_default_document_ids
    )

    global_tag_ids = fields.Many2many(
        comodel_name='clv.global_tag',
        relation='clv_document_mass_edit_global_tag_rel',
        column1='document_id',
        column2='global_tag_id',
        string='Global Tags'
    )
    global_tag_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Global Tags:', default=False, readonly=False, required=False
    )

    category_ids = fields.Many2many(
        comodel_name='clv.document.category',
        relation='clv_document_mass_edit_category_rel',
        column1='document_id',
        column2='category_id',
        string='Categories'
    )
    category_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Categories:', default=False, readonly=False, required=False
    )

    document_type_id = fields.Many2one(
        comodel_name='clv.document.type',
        string='Documnent Type'
    )
    document_type_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Documnent Type:', default=False, readonly=False, required=False
    )

    base_document_id = fields.Many2one(
        comodel_name='clv.document',
        string='Base Document'
    )
    base_document_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Base Document:', default=False, readonly=False, required=False
    )

    date_document = fields.Date(string='Document Date', default=False, readonly=False, required=False)
    date_document_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Document Date:', default=False, readonly=False, required=False
    )

    date_foreseen = fields.Date(string='Foreseen Date', default=False, readonly=False, required=False)
    date_foreseen_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Foreseen Date:', default=False, readonly=False, required=False
    )

    date_deadline = fields.Date(string='Deadline', default=False, readonly=False, required=False)
    date_deadline_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Deadline:', default=False, readonly=False, required=False
    )

    @api.model
    def referenceable_models(self):
        return [(ref.model, ref.name) for ref in self.env['clv.referenceable.model'].search([
            ('base_model', '=', 'clv.document'),
        ])]

    ref_id = fields.Reference(
        selection='referenceable_models',
        string='Refers to')
    ref_id_selection = fields.Selection(
        [('set', 'Set'),
         ('remove', 'Remove'),
         ], string='Refers to:', default=False, readonly=False, required=False
    )

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
    def do_document_mass_edit(self):
        self.ensure_one()

        for document in self.document_ids:

            _logger.info(u'%s %s', '>>>>>', document.name)

            if self.global_tag_ids_selection == 'add':
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((4, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.global_tag_ids = m2m_list
            if self.global_tag_ids_selection == 'remove_m2m':
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((3, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.global_tag_ids = m2m_list
            if self.global_tag_ids_selection == 'set':
                m2m_list = []
                for global_tag_id in document.global_tag_ids:
                    m2m_list.append((3, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.global_tag_ids = m2m_list
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((4, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.global_tag_ids = m2m_list

            if self.category_ids_selection == 'add':
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((4, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.category_ids = m2m_list
            if self.category_ids_selection == 'remove_m2m':
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((3, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.category_ids = m2m_list
            if self.category_ids_selection == 'set':
                m2m_list = []
                for category_id in document.category_ids:
                    m2m_list.append((3, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.category_ids = m2m_list
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((4, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                document.category_ids = m2m_list

            if self.document_type_id_selection == 'set':
                document.document_type_id = self.document_type_id.id
            if self.document_type_id_selection == 'remove':
                document.document_type_id = False

            if self.base_document_id_selection == 'set':
                document.base_document_id = self.base_document_id.id
            if self.base_document_id_selection == 'remove':
                document.base_document_id = False

            if self.date_document_selection == 'set':
                document.date_document = self.date_document
            if self.date_document_selection == 'remove':
                document.date_document = False

            if self.date_foreseen_selection == 'set':
                document.date_foreseen = self.date_foreseen
            if self.date_foreseen_selection == 'remove':
                document.date_foreseen = False

            if self.date_deadline_selection == 'set':
                document.date_deadline = self.date_deadline
            if self.date_deadline_selection == 'remove':
                document.date_deadline = False

            if self.ref_id_selection == 'set':
                document.ref_id = self.ref_id
            if self.ref_id_selection == 'remove':
                document.ref_id = False

        return True
