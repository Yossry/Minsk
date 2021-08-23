# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Address History (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Address History Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_address_jcafb',
    ],
    'data': [
        # 'views/address_view.xml',
        'views/employee_view.xml',
        'views/address_history_reg_state_view.xml',
        'views/address_history_state_view.xml',
        'views/address_history_menu_view.xml',
        'wizard/address_history_updt_view.xml',
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
