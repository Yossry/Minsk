# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Family (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Family Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_jcafb',
        'clv_family',
        'clv_family_history',
        'clv_document',
    ],
    'data': [
        'data/family_seq.xml',
        'data/document.xml',
        'views/family_view.xml',
        'views/document_view.xml',
        'views/family_code_view.xml',
        'views/family_reg_state_view.xml',
        'views/family_state_view.xml',
        'views/address_view.xml',
        'views/family_menu_view.xml',
        'wizard/family_mass_edit_view.xml',
        'wizard/family_document_setup_view.xml',
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
