# Copyright 2018-2019 UNIBRAVO
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Bravo Backend Theme v12",
    "summary": "Full Responsive Bravo Backend Theme for Odoo v12.0",
    "version": "12.0.1.0",
    "category": "Themes/Backend",
    "website": "https://gwww.unibravo.com",
    "author": "UNIBRAVO",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": [],
    "depends": ['web'],
    "qweb": ['static/src/xml/*.xml'],
    "data": [
        'views/assets.xml',
        'views/web.xml',
    ],

    "price": 50,
    'currency': 'EUR',
    'live_test_url': 'http://212.237.62.27:8012/web?db=odoo12-bravo',
}
