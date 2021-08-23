# -*- coding: utf-8 -*-
{
    'name': "ventas_monopark",

    'summary': """      
        Functions and methods for the sale module view and adjustments in the sales quotation report""",

    'description': """
        Functions for the sale modules
    """,

    'author': "Xmarts",
    'collaborators': "Gilberto Santiago Acevedo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/report_cot.xml',
        'report/report_pago.xml',
        #'report/anexo_ventas.xml',
        #'report/pedido_confirmado.xml',
        #'report/layout.xml',
        #'report/rep_cot_anexo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}