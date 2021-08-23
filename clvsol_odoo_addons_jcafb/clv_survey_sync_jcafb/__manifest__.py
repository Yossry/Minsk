# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Survey External Sync (for CLVhealth-JCAFB Solution)',
    'summary': 'Survey External Sync Module used in CLVhealth-JCAFB Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'CLVsol Solutions',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'depends': [
        'clv_survey',
        'clv_external_sync',
    ],
    'data': [
        'data/survey_stage_sync.xml',
        'data/survey_survey_sync.xml',
        'data/survey_page_sync.xml',
        'data/survey_question_sync.xml',
        'data/survey_label_sync.xml',
        'data/survey_user_input_sync.xml',
        'data/survey_user_input_line_sync.xml',
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
