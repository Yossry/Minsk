# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import shutil

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MfileArchive(models.TransientModel):
    _description = 'Media File Archive'
    _name = 'clv.mfile.archive'

    def _default_mfile_ids(self):
        return self._context.get('active_ids')
    mfile_ids = fields.Many2many(
        comodel_name='clv.mfile',
        relation='clv_mfile_mfile_archive_rel',
        string='Media Files',
        default=_default_mfile_ids
    )

    def _default_directory_id(self):
        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('name', '=', 'Survey Files (Input)'),
        ])
        directory_id = file_system_directory.id
        return directory_id
    directory_id = fields.Many2one(
        comodel_name='clv.file_system.directory',
        string='Directory',
        default=_default_directory_id,
        required="True"
    )

    def _default_archive_directory_id(self):
        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('name', '=', 'Survey Files (Archive)'),
        ])
        directory_id = file_system_directory.id
        return directory_id
    archive_directory_id = fields.Many2one(
        comodel_name='clv.file_system.directory',
        string='Archive Directory',
        default=_default_archive_directory_id,
        required="True"
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
    def do_mfile_archive(self):
        self.ensure_one()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('id', '=', self.directory_id.id),
        ])
        archive_file_system_directory = FileSystemDirectory.search([
            ('id', '=', self.archive_directory_id.id),
        ])

        for mfile in self.mfile_ids:

            filepath = file_system_directory.directory + '/' + mfile.name
            archive_filepath = archive_file_system_directory.directory + '/' + mfile.name

            _logger.info(u'%s %s', '>>>>>', mfile.name)

            if mfile.state == 'imported':

                shutil.move(filepath, archive_filepath)

                mfile.directory_id = archive_file_system_directory.id
                mfile.file_name = mfile.name
                mfile.stored_file_name = mfile.name

                mfile.state = 'archived'

        return True
