# -*- coding: utf-8 -*-
{
    'name': "reporte_factura",

    'summary': """
        Module to give design to the invoices report""",

    'description': """
        Module to give design to the invoices report and show information both of the client and the company
    """,

    'author': "Xmarts",
    'Collaborator': "Gilberto Santiago Acevedo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reporte/reporte_factura.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}