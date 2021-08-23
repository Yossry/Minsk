# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Family (Aux) (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Family (Aux) Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_jcafb',
        'clv_family_aux',
        'clv_document',
    ],
    'data': [
        'data/document.xml',
        'views/document_view.xml',
        'views/family_aux_reg_state_view.xml',
        'views/family_aux_state_view.xml',
        'views/family_aux_menu_view.xml',
        'wizard/family_aux_mass_edit_view.xml',
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
