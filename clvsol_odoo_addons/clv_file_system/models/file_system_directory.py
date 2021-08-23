# -*- coding: utf-8 -*-
# Copyright 2017-2018 Onestein (<http://www.onestein.eu>)
# Copyright (C) 2017-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from os.path import join, exists

from odoo import api, fields, models, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class FileSystemDirectory(models.Model):
    _name = 'clv.file_system.directory'
    _description = 'File System Directory'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        copy=False
    )
    description = fields.Char(string='Description')
    notes = fields.Text(string='Notes')

    directory = fields.Char(
        string='Directory',
        required=True,
    )

    active = fields.Boolean(string='Active', default=1)

    @api.multi
    def get_dir(self):
        self.ensure_one()
        directory = self.directory or ''
        # adds slash character at the end if missing
        return join(directory, '')

    @api.onchange('directory')
    def onchange_directory(self):
        if self.directory and not exists(self.directory):
            raise Warning(_('Directory does not exist'))

    @api.multi
    def reload(self):
        self.onchange_directory()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super().copy(default=default)
