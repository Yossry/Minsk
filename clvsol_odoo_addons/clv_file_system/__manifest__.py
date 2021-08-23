# -*- coding: utf-8 -*-
# Copyright 2017-2018 Onestein (<http://www.onestein.eu>)
# Copyright (C) 2017-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'File System',
    'summary': 'File System Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
    ],
    'data': [
        'security/file_system_security.xml',
        'security/ir.model.access.csv',
        'views/file_system_directory_view.xml',
        'views/file_system_file_view.xml',
        'wizard/file_system_directory_file_upload_view.xml',
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
