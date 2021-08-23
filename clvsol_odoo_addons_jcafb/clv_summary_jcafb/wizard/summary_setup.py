# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SummarySetUp(models.TransientModel):
    _description = 'Summary SetUp'
    _name = 'clv.summary.summary_setup'

    def _default_summary_ids(self):
        return self._context.get('active_ids')
    summary_ids = fields.Many2many(
        comodel_name='clv.summary',
        relation='clv_summary_summary_setup_rel',
        string='Summaries',
        default=_default_summary_ids
    )

    def _default_dir_path(self):
        file_store_path = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_filestore_path', '').strip()
        summary_files_directory = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_summary_files_directory', '').strip()
        return file_store_path + '/' + summary_files_directory
    dir_path = fields.Char(
        string='Directory Path',
        required=True,
        help="Directory Path",
        default=_default_dir_path
    )

    def _default_file_name(self):
        summary_file_name = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_summary_file_name', '').strip()
        return summary_file_name
    file_name = fields.Char(
        string='File Name',
        required=True,
        help="File Name",
        default=_default_file_name
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
    def do_summary_setup(self):
        self.ensure_one()

        for summary in self.summary_ids:

            reference = summary.reference
            model = summary.model
            reference_id = reference[len(model) + 1:]

            _logger.info(u'%s %s', '>>>>>', reference)
            _logger.info(u'%s %s', '>>>>>>>>>>', model)

            if summary.model == 'clv.address':
                Address = self.env['clv.address']
                address = Address.search([('id', '=', reference_id)])
                address._address_summary_setup(self.dir_path, self.file_name)

            if summary.model == 'clv.family':
                Family = self.env['clv.family']
                family = Family.search([('id', '=', reference_id)])
                family._family_summary_setup(self.dir_path, self.file_name)

            if summary.model == 'clv.person':
                Person = self.env['clv.person']
                person = Person.search([('id', '=', reference_id)])
                person._person_summary_setup(self.dir_path, self.file_name)

            if summary.model == 'clv.person_aux':
                PersonAux = self.env['clv.person_aux']
                person_aux = PersonAux.search([('id', '=', reference_id)])
                person_aux._person_aux_summary_setup(self.dir_path, self.file_name)

            if summary.model == 'hr.employee':
                Employee = self.env['hr.employee']
                employee = Employee.search([('id', '=', reference_id)])
                employee._employee_summary_setup(self.dir_path, self.file_name)

        return True

    @api.multi
    def do_populate_all_summaries(self):
        self.ensure_one()

        Summary = self.env['clv.summary']
        summaries = Summary.search([])

        self.summary_ids = summaries

        return self._reopen_form()
