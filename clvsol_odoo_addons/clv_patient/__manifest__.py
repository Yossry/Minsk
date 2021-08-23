# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Patient',
    'summary': 'Patient Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_base',
        'clv_global_log',
        'clv_entity',
        'clv_global_tag',
    ],
    'data': [
        'security/patient_security.xml',
        'security/ir.model.access.csv',
        'views/patient_view.xml',
        'views/patient_log_view.xml',
        'views/patient_category_view.xml',
        'views/patient_category_log_view.xml',
        'views/res_partner_view.xml',
        'views/global_tag_view.xml',
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
