# -*- coding: utf-8 -*-
{
    'name': 'CRM Dashboard for Marketing Executive',
    'version': '1.0',
    'category': 'Sales',
    'price': 17.99,
    'currency': 'EUR',
    'author': 'Zadsolutions, Ahmed Hefni',
    'website': "http://zadsolutions.com",
    'summary': """
    These dashboards make it easy for people in various sales and marketing roles to gauge the state of campaigns, leads, and opportunities for their organization, teams, or themselves.
    """,
    'depends': [
        'crm','sale_management'
    ],
    'data': [
        "views/templates.xml",
        "views/sales_markting_cost_view.xml",
        "views/crm_dashboard_view.xml",
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
}
