# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models


class ObjectModelExport(models.AbstractModel):
    _inherit = 'clv.object.model_export'

    def model_export_dir_path(self, export_type):
        if export_type == 'xls':
            return '/opt/openerp/filestore/pbm/export/xls'
        if export_type == 'sqlite':
            return '/opt/openerp/filestore/pbm/export/sqlite'
        return False
