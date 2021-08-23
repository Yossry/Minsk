# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Module (customizations for CLVhealth-PBM Solution)',
    'summary': 'Base Module Module customizations for CLVhealth-PBM Solution.',
    'version': '4.0.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base',
        'contacts',
        'base_address_city',
    ],
    'data': [
        'views/base_address_city_menu_view.xml',
        'views/base_menu_view.xml',
        'views/referenciable_model_menu_view.xml',
        'views/global_settings_menu_view.xml',
        'views/mfile_menu_view.xml',
        'views/community_menu_view.xml',
        'views/insurance_menu_view.xml',
        'views/health_menu_view.xml',
        'views/export_menu_view.xml',
        'views/report_menu_view.xml',
        'views/external_sync_menu_view.xml',
        'views/verification_menu_view.xml',
        'views/processing_menu_view.xml',
        'data/annotation_seq.xml',
        'data/global_settings_filestore.xml',
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
