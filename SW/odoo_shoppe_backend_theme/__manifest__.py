# -*- coding: utf-8 -*-
####################################################################################
#    QPR Qatar Pvt. Ltd.
#    Copyright (C) 2018-TODAY
#    Author: Abhishek (<https://www.qpr.qa>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': "Odoo QPR Backend Theme",
    'version': '1.0',
    'summary': 'Odoo QPR Theme v12',
    'description': """
QPR Odoo Backend Theme
================================
    """,
    'license': 'OPL-1',
    'author': "QPR Backend-Theme",
    'website': "http://www.qpr.qa",
    'images': ['static/description/odooshoppe_backend_theme.jpg',
               'static/description/odooshoppe_backend_theme_screenshot.jpg'],
    'category': 'Theme/Backend',
    'depends': ['base', 'mail', 'calendar', 'website'],
    'data': [
        'views/enterprise_theme_templates.xml',
        'views/sidebar_theme_templates.xml',
        'views/ir_ui_view_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'data/data.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'application': True,
}
