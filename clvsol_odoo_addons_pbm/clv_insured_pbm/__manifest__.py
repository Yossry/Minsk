# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Insured (customizations for CLVhealth-PBM Solution)',
    'summary': 'Insured Module customizations for CLVhealth-PBM Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_pbm',
        'clv_insured',
        'clv_document',
        'clv_set',
    ],
    'data': [
        'data/insured_seq.xml',
        'data/document.xml',
        'views/insured_code_view.xml',
        'views/document_view.xml',
        'views/set_element_view.xml',
        'views/insured_reg_state_view.xml',
        'views/insured_state_view.xml',
        'views/insured_menu_view.xml',
        'wizard/insured_associate_to_set_view.xml',
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
