# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Address (customizations for CLVhealth-PBM Solution)',
    'summary': 'Address Module customizations for CLVhealth-PBM Solution.',
    'version': '4.0.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_pbm',
        'clv_address',
    ],
    'data': [
        'data/address_seq.xml',
        'views/address_code_view.xml',
        'views/address_reg_state_view.xml',
        'views/address_state_view.xml',
        'views/address_menu_view.xml',
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
