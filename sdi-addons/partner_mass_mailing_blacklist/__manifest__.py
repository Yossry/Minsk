###############################################################################
#
#    SDi Soluciones Informáticas
#    Copyright (C) 2020-Today SDi Soluciones Informáticas <www.sdi.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Partner Mass Mailing Blacklist',
    'summary': 'Add button in partner form view to add email to blacklist',
    'author': 'Jorge Luis Quinteros, SDi Soluciones Informáticas',
    'website': 'https://sdi.web.sdi.es/odoo/',
    'license': 'LGPL-3',
    'category': 'Mail',
    'version': '12.0.1.0.0',
    'depends': [
        'contacts',
        'mass_mailing',
    ],
    'data': [
        'views/res_partner_views.xml',
    ],
}
