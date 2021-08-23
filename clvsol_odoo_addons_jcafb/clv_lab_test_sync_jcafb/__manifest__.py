# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Lab Test External Sync (for CLVhealth-JCAFB Solution)',
    'summary': 'Lab Test External Sync Module used in CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_lab_test_jcafb',
        'clv_external_sync',
    ],
    'data': [
        'data/lab_test_unit_sync.xml',
        'data/lab_test_type_sync.xml',
        'data/lab_test_request_sync.xml',
        'data/lab_test_result_sync.xml',
        'data/lab_test_report_sync.xml',
        'data/lab_test_criterion_sync.xml',
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
