# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Patient (customizations for CLVhealth-JCAFB Solution)',
    'summary': 'Patient Module customizations for CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base_jcafb',
        'clv_patient',
        'clv_document',
        'clv_community',
        'clv_event',
        'clv_lab_test',
    ],
    'data': [
        'data/document.xml',
        'data/community_member.xml',
        'data/event_attendee.xml',
        'data/lab_test.xml',
        'views/document_view.xml',
        'views/community_member_view.xml',
        'views/event_attendee_view.xml',
        'views/lab_test_view.xml',
        'views/patient_menu_view.xml',
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
