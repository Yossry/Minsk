# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
from os import listdir
from os.path import isfile, join, exists, normpath, realpath
import base64


from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.tools import human_size

_logger = logging.getLogger(__name__)


class FileSystemFile(models.Model):
    _name = 'clv.file_system.file'
    _description = 'File System File'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True
    )
    file_name = fields.Char(string='File Name')
    file_content = fields.Binary(
        string='File Content',
        compute='_compute_file'
    )
    stored_file_name = fields.Char(string='Stored File Name')
    directory_id = fields.Many2one(
        comodel_name='clv.file_system.directory',
        string='Directory'
    )

    active = fields.Boolean(string='Active', default=1)

    @api.multi
    def _file_read(self, fname, bin_size=False):

        def file_not_found(fname):
            raise Warning(_(
                '''Error while reading file %s.
                Maybe it was removed or permission is changed.
                Please refresh the list.''' % fname))

        self.ensure_one()
        r = ''
        directory = self.directory_id.get_dir() or ''
        full_path = directory + fname
        if not (directory and os.path.isfile(full_path)):
            # file_not_found(fname)
            return False
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = base64.b64encode(open(full_path, 'rb').read())
        except (IOError, OSError):
            _logger.info("_read_file reading %s", fname, exc_info=True)
        return r

    @api.depends('stored_file_name')
    def _compute_file(self):
        bin_size = self._context.get('bin_size')
        for file in self:
            if file.stored_file_name:
                content = file._file_read(file.stored_file_name, bin_size)
                file.file_content = content


class FileSystemDirectory(models.Model):
    _inherit = 'clv.file_system.directory'

    file_ids = fields.One2many(
        comodel_name='clv.file_system.file',
        compute='_compute_file_ids',
        string='Files'
    )
    file_count = fields.Integer(compute='_file_count', string="# Files")

    @api.multi
    def _compute_file_ids(self):
        File = self.env['clv.file_system.file']
        for directory in self:
            # directory.file_ids = None
            if directory.get_dir():
                for file_name in directory._get_directory_files():
                    file = File.search([
                        ('file_name', '=', file_name),
                        ('directory_id', '=', directory.id),
                    ])
                    if file.id is False:
                        directory.file_ids += File.create({
                            'name': file_name,
                            'file_name': file_name,
                            'stored_file_name': file_name,
                            'directory_id': directory.id,
                        })
                    else:
                        directory.file_ids += file

    @api.multi
    def _file_count(self):
        for directory in self:
            directory.file_count = len(directory.file_ids)

    @api.multi
    def _get_directory_files(self):

        def get_files(directory, files):
            for file_name in listdir(directory):
                full_path = join(directory, file_name)

                # Symbolic links and up-level references are not considered
                norm_path = normpath(realpath(full_path))
                if norm_path in full_path:
                    if isfile(full_path) and file_name[0] != '.':
                        files.append(file_name)

        self.ensure_one()
        files = []
        if self.get_dir() and exists(self.get_dir()):
            try:
                get_files(self.get_dir(), files)
            except (IOError, OSError):
                _logger.info(
                    "_get_directory_files reading %s",
                    self.get_dir(),
                    exc_info=True
                )
        return files
