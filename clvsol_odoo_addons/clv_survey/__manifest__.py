# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Survey',
    'summary': 'Survey Module used by CLVsol Solutions.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'survey',
        'clv_base',
    ],
    'data': [
        'security/survey_security.xml',
        'views/survey_survey_view.xml',
        'views/survey_page_view.xml',
        'views/survey_question_view.xml',
        'views/survey_label_view.xml',
        'wizard/survey_duplicate_view.xml',
        'wizard/survey_code_renew_view.xml',
        'wizard/survey_export_xls_view.xml',
        'wizard/survey_export_xml_view.xml',
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
