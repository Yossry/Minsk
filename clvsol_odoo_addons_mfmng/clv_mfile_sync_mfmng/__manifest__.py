# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Media File External Sync (for Media File Management Solution)',
    'summary': 'Media File External Sync Module used in Media File Management Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_mfmng',
        'clv_mfile',
        'clv_external_sync',
    ],
    'data': [
        'data/mfile_marker_sync.xml',
        'data/mfile_category_sync.xml',
        'data/mfile_format_sync.xml',
        'data/mfile_sync.xml',
    ],
    'demo': [],
    'test': [],
    'init_xml': [],
    'test': [],
    'update_xml': [],
    'installable': True,
    'application': False,
    'active': False,
    'css': [],
}
