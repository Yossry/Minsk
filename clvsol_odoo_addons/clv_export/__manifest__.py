# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Export',
    'summary': 'Export Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
        'clv_file_system',
        'clv_set',
    ],
    'data': [
        'security/export_security.xml',
        'security/ir.model.access.csv',
        'views/model_export_method_view.xml',
        'views/model_export_template_view.xml',
        'views/model_export_template_field_view.xml',
        'views/model_export_view.xml',
        'views/model_export_field_view.xml',
        'views/global_settings_view.xml',
        'views/set_view.xml',
        'wizard/model_export_refresh_view.xml',
        'wizard/model_export_execute_view.xml',
        'wizard/model_export_template_duplicate_view.xml',
        'wizard/model_export_template_field_copy_view.xml',
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
