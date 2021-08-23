# -*- coding: utf-8 -*-
{
    'name': 'Tracking',
    'category': 'Hidden',
    'version': '0.1',
    'author' : 'Xmarts',
    'description':
        """
Odoo Web Tracking module.
========================
This module provides the lxtrack of the Odoo Web Client.
        """,
    'depends': ['base','sale','purchase','stock','delivery','hr','base_geolocalize','contacts','point_of_sale','pos_save_quotations','product','account'],
    'auto_install': True,
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/partner.xml',
        #'views/sale_views.xml',
        #'views/stock_picking.xml',
        'views/zona.xml',
        'views/zona2.xml',
        #'views/stock_move.xml',
        'views/route_orders_views.xml',
        'views/hr_employee.xml',
        #'reports/layout.xml',
        'wizard/partner_process.xml',
        'views/pricelist.xml',
        'views/pos_quotation_view.xml',
        'views/quotation_pos_report.xml',
        'report/reporte_carga.xml'
    ],
    'bootstrap': True,
}
