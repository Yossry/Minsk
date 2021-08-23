# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def modification_date(filepath):
    t = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(t)


class MfileNewFilesSearch(models.TransientModel):
    _description = 'Media File - New Files Search'
    _name = 'clv.mfile.new_files_search'

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

    def _default_phase_id(self):
        phase_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_phase_id', '').strip())
        return phase_id
    phase_id = fields.Many2one(
        comodel_name='clv.phase',
        string='Phase',
        default=_default_phase_id,
        ondelete='restrict'
    )

    @api.multi
    def do_mfile_new_files_search(self):
        self.ensure_one()

        FileSystemDirectory = self.env['clv.file_system.directory']
        file_system_directory = FileSystemDirectory.search([
            ('id', '=', self.directory_id.id),
        ])

        MFile = self.env['clv.mfile']

        listdir = os.listdir(file_system_directory.directory)

        for mfile_name in listdir:

            _logger.info(u'%s %s', '>>>>>', mfile_name)

            mfile = MFile.search([
                ('name', '=', mfile_name),
            ])

            _logger.info(u'%s %s', '>>>>>>>>>>', mfile.name)

            if mfile.id is False:

                values = {}
                values['name'] = mfile_name
                values['phase_id'] = self.phase_id.id
                values['directory_id'] = file_system_directory.id
                values['file_name'] = mfile_name
                values['stored_file_name'] = mfile_name
                _logger.info(u'%s %s', '>>>>>>>>>>', values)
                mfile.create(values)

        return True
