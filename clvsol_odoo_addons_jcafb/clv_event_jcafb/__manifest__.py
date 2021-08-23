# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Event (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Event Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_event',
        'clv_employee',
    ],
    'data': [
        # 'views/event_view.xml',
        'views/event_code_view.xml',
        'views/event_state_view.xml',
        'views/event_attendee_reg_state_view.xml',
        'data/event_seq.xml',
        # 'wizard/event_updt_view.xml',
        'views/event_menu_view.xml',
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
