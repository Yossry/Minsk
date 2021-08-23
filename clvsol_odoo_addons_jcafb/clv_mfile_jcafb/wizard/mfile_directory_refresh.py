# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os.path

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MfileDirectoryRefresh(models.TransientModel):
    _name = 'clv.mfile.directory_refresh'

    dir_path = fields.Char(
        'Directory Path (Input)',
        required=True,
        help="Input Directory Path",
        default='/opt/openerp/clvsol_clvhealth_jcafb/survey_files/input'
    )

    archive_dir_path = fields.Char(
        'Directory Path (Archive)',
        required=True,
        help="Archive Directory Path",
        default='/opt/openerp/clvsol_clvhealth_jcafb/survey_files/archive'
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
    def do_mfile_directory_refresh(self):
        self.ensure_one()

        MFile = self.env['clv.mfile']
        media_files = MFile.search([])

        FileSystemDirectory = self.env['clv.file_system.directory']
        directory = FileSystemDirectory.search([
            ('directory', '=', self.dir_path),
        ])
        archive_directory = FileSystemDirectory.search([
            ('directory', '=', self.archive_dir_path),
        ])

        for media_file in media_files:

            _logger.info(u'%s %s', '>>>>>', media_file.name)

            filepath = self.dir_path + '/' + media_file.name
            archive_filepath = self.archive_dir_path + '/' + media_file.name

            if os.path.isfile(filepath):
                media_file.directory_id = directory.id
                _logger.info(u'%s %s', '>>>>>>>>>>', filepath)

            if os.path.isfile(archive_filepath):
                media_file.directory_id = archive_directory.id
                _logger.info(u'%s %s', '>>>>>>>>>>', archive_filepath)

        return True
