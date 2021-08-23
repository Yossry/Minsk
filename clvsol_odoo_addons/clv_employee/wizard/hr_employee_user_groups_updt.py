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


class EmployeeUserGroupsEdit(models.TransientModel):
    _description = 'Employee User Groups Updt'
    _name = 'hr.employee.user_groups_updt'

    def _default_employee_ids(self):
        return self._context.get('active_ids')
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='hr_employee_user_groups_updt_rel',
        string='Employees',
        default=_default_employee_ids
    )
    count_employees = fields.Integer(
        string='Number of Employees',
        compute='_compute_count_employees',
        store=False
    )

    ref_employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Reference Employee'
    )

    group_ids = fields.Many2many(
        comodel_name='res.groups',
        relation='hr_employee_updt_group_rel',
        column1='employee_id',
        column2='group_id',
        string='Access Rights'
    )
    group_ids_selection = fields.Selection(
        [('add', 'Add'),
         ('remove_m2m', 'Remove'),
         ('set', 'Set'),
         ], string='Access Rights:', default=False, readonly=False, required=False
    )

    @api.depends('employee_ids')
    def _compute_count_employees(self):
        for r in self:
            r.count_employees = len(r.employee_ids)

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
    def do_employee_user_groups_updt(self):
        self.ensure_one()

        _logger.info(u'Employee User Groups Update on %s', self.employee_ids.ids)

        for employee_reg in self.employee_ids:

            _logger.info(u'%s %s', employee_reg.id, employee_reg.name)

            if employee_reg.user_id is not False:

                if self.group_ids_selection == 'add':
                    for group in self.group_ids:
                        values = {
                            'groups_id': [(4, group.id)],
                        }
                        employee_reg.user_id.write(values)
                if self.group_ids_selection == 'remove_m2m':
                    for group in self.group_ids:
                        values = {
                            'groups_id': [(3, group.id)],
                        }
                        employee_reg.user_id.write(values)
                if self.group_ids_selection == 'set':
                    values = {
                        'groups_id': [(6, 0, [])],
                    }
                    employee_reg.user_id.write(values)

                    for group in self.group_ids:
                        values = {
                            'groups_id': [(4, group.id)],
                        }
                        employee_reg.user_id.write(values)

        return True

    @api.multi
    def get_reference_Employee_access_rights(self):
        self.ensure_one()

        if self.ref_employee_id.user_id is not False:
            group_ids = []
            for group in self.ref_employee_id.user_id.groups_id:
                _logger.info(u'%s %s', group.id, group.name)
                group_ids.append(group.id)
            self.group_ids = group_ids

        return self._reopen_form()

    @api.multi
    def do_refresh_access_rights(self):
        self.ensure_one()

        return self._reopen_form()
