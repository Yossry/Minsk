# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Processing',
    'summary': 'Processing Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
        'clv_global_log',
    ],
    'data': [
        'security/processing_security.xml',
        'security/ir.model.access.csv',
        'views/processing_host_view.xml',
        'views/processing_host_log_view.xml',
        'views/processing_template_view.xml',
        'views/processing_template_log_view.xml',
        'views/processing_schedule_view.xml',
        'views/processing_schedule_log_view.xml',
        # 'views/processing_batch_view.xml',
        # 'views/processing_batch_log_view.xml',
        # 'views/processing_batch_member_view.xml',
        # 'views/referenceable_model_view.xml',
        # 'data/processing_batch_member.xml',
        'wizard/processing_schedule_exec_view.xml',
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
