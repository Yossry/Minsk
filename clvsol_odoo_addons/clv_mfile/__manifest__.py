# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Media File',
    'summary': 'Media File Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
        'clv_global_log',
        'clv_global_tag',
    ],
    'data': [
        'security/mfile_security.xml',
        'security/ir.model.access.csv',
        'views/mfile_view.xml',
        'views/mfile_category_view.xml',
        'views/mfile_marker_view.xml',
        'views/global_tag_view.xml',
        'views/mfile_format_view.xml',
        # 'views/mfile_annotation_view.xml',
        'views/mfile_kanban_view.xml',
        'views/mfile_log_view.xml',
        'wizard/mfile_mass_edit_view.xml',
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
