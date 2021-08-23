# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Person History (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Person History Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_person_jcafb',
    ],
    'data': [
        # 'views/person_view.xml',
        'views/person_history_reg_state_view.xml',
        'views/person_history_state_view.xml',
        'views/person_history_menu_view.xml',
        'wizard/person_history_updt_view.xml',
        'wizard/person_history_person_associate_to_set_view.xml',
        'wizard/person_history_person_mass_edit_view.xml',
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
