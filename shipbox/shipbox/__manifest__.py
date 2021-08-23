# © 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'ShipBox',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'depends': [
        'stock',
        'delivery',
    ],
    'author': 'Hibou Corp.',
    'license': 'AGPL-3',
    'website': 'https://hibou.io/',
    'data': [
        'security/ir.model.access.csv',
        'views/webclient_templates.xml',
        'views/res_users_views.xml',
        'views/stock_views.xml',
    ],
    'qweb': [
    'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': False,
}
