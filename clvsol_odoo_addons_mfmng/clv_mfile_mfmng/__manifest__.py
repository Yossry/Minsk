# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Media File (customizations for Media File Management Solution)',
    'summary': 'Media File Module customizations for Media File Management Solution.',
    'version': '12.0.4.0',
    'author': 'Carlos Eduardo Vercelino - CLVsol',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'website': 'https://github.com/CLVsol',
    'images': [],
    'depends': [
        'clv_base_mfmng',
        'clv_mfile',
    ],
    'data': [
        'views/mfile_code_view.xml',
        'views/mfile_reg_state_view.xml',
        'views/mfile_state_view.xml',
        'data/mfile_seq_03.xml',
        'data/mfile_seq_04.xml',
        'data/mfile_seq_06.xml',
        'data/mfile_seq_09.xml',
        'data/mfile_seq_10.xml',
        'wizard/mfile_mass_edit_view.xml',
        'views/mfile_menu_view.xml',
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
