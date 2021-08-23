# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Point of Sale Enhancement',
    'version': '1.0',
    'category': 'Point of Sale Enhancement',
    'sequence': 6,
    'summary': 'QPR point of sale',
    'description': """

- Receipt improvement
""",
    'depends': ['point_of_sale'],
    'data': [
        'views/product_views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
