# coding: utf-8
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Company Wizard - Base Module',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'summary': "Provide Wizard to create new companies more easily",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/view_res_company.xml',
        'views/view_res_company_create_wizard.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_groups.xml',
    ],
    'installable': True,
}
