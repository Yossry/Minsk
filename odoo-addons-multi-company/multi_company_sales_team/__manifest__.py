# coding: utf-8
# Copyright (C) 2014-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Multi Company - Sales Team Module',
    'version': '10.0.1.0.0',
    'category': 'Multi Company',
    'summary': 'Handle Multi company for Sales Team Module',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'multi_company_base',
        'sales_team',
    ],
    'data': [
        'views/view_crm_team.xml',
    ],
    'installable': True,
}
