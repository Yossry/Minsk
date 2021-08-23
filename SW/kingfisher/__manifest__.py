# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kingfisher Theme',
    'description': '''Kingfisher Theme
odoo ecommerce theme
odoo ecommerce themes
odoo webshop theme
ecommerce theme for odoo store
odoo responsive themes
responsive odoo ecommerce theme
responsive ecommerce odoo theme
responsive odoo webshop theme
odoo bootstrap theme
html5 bootstrap theme
html5 bootstrap theme for odoo
responsive bootstrap theme
responsive bootstrap theme for odoo
odoo ecommerce templates
odoo website themes
odoo ecommerce website theme
odoo theme for ecommerce store
customize odoo theme
odoo theme for business
odoo business theme
responsive bootstrap business theme
Kingfisher Theme
Odoo Kingfisher Theme
Kingfisher theme for Odoo
odoo custom theme
customizable odoo theme
odoo multipurpose theme
odoo 11 theme
multipurpose theme
odoo multipurpose theme
odoo responsive theme
responsive theme
odoo theme
odoo themes
ecommerce theme
odoo ecommerce themes
odoo website themes
odoo bootstrap themes
bootstrap themes
bootstrap theme
customize odoo theme
ecommerce store theme
theme for business
theme for ecommerce store
    ''',
    'category': 'Theme/Ecommerce',
    'version': '12.0.1.0.1',
    'license': 'OPL-1',
    'author': 'AppJetty',
    'website': 'https://www.appjetty.com',
    'depends': [
                'website_theme_install',
                'website_sale',
                'sale_management',
                'mass_mailing',
                'website_blog',
    ],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/view.xml',
        'views/website_view.xml',
        'views/slider_view.xml',
        'views/snippets.xml',
        'views/theme_customize.xml',
        'views/theme.xml',
    ],
    'support': 'support@appjetty.com',
    'application': True,
    'live_test_url': 'http://theme-kingfisher-v10.appjetty.com',
    'images': [
        'static/description/splash-screen.png',
        'static/description/splash-screen_screenshot.png',
    ],
    'price': 99.00,
    'currency': 'EUR',
}
