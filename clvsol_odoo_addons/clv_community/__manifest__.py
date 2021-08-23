# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Community',
    'summary': 'Community Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base',
        'clv_global_log',
        'clv_global_tag',
    ],
    'data': [
        'security/community_security.xml',
        'security/ir.model.access.csv',
        'views/community_view.xml',
        'views/community_log_view.xml',
        'views/community_category_view.xml',
        'views/community_category_log_view.xml',
        'views/global_tag_view.xml',
        'views/community_member_view.xml',
        'views/referenceable_model_view.xml',
        # 'wizard/community_updt_view.xml',
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
