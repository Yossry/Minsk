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


class EventUpdate(models.TransientModel):
    _name = 'clv.event.updt'

    def _default_event_ids(self):
        return self._context.get('active_ids')
    event_ids = fields.Many2many(
        comodel_name='clv.event',
        relation='clv_event_updt_rel',
        string='Events',
        default=_default_event_ids
    )

    global_tag_ids = fields.Many2many(
        comodel_name='clv.global_tag',
        relation='clv_event_updt_global_tag_rel',
        column1='event_id',
        column2='global_tag_id',
        string='Global Tags'
    )
    global_tag_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Global Tags', default=False, readonly=False, required=False
    )

    category_ids = fields.Many2many(
        comodel_name='clv.event.category',
        relation='clv_event_updt_category_rel',
        column1='event_id',
        column2='category_id',
        string='Categories'
    )
    category_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Categories', default=False, readonly=False, required=False
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
    def do_event_updt(self):
        self.ensure_one()

        for event in self.event_ids:

            _logger.info(u'%s %s', '>>>>>', event.name)

            if self.global_tag_ids_selection == 'add':
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((4, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.global_tag_ids = m2m_list
            if self.global_tag_ids_selection == 'remove_m2m':
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((3, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.global_tag_ids = m2m_list
            if self.global_tag_ids_selection == 'set':
                m2m_list = []
                for global_tag_id in event.global_tag_ids:
                    m2m_list.append((3, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.global_tag_ids = m2m_list
                m2m_list = []
                for global_tag_id in self.global_tag_ids:
                    m2m_list.append((4, global_tag_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.global_tag_ids = m2m_list

            if self.category_ids_selection == 'add':
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((4, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.category_ids = m2m_list
            if self.category_ids_selection == 'remove_m2m':
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((3, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.category_ids = m2m_list
            if self.category_ids_selection == 'set':
                m2m_list = []
                for category_id in event.category_ids:
                    m2m_list.append((3, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.category_ids = m2m_list
                m2m_list = []
                for category_id in self.category_ids:
                    m2m_list.append((4, category_id.id))
                _logger.info(u'%s %s', '>>>>>>>>>>', m2m_list)
                event.category_ids = m2m_list

        return True
