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
    'name': 'Contract Contract Invoice Partner',
    'summary': 'Select invoice partner from sale order to the new contract',
    'author': 'Oscar Soto, SDi Soluciones Informáticas',
    'website': 'https://www.sdi.es/odoo/',
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '12.0.1.0.0',
    'depends': [
        'contract',
        'sale_management',
        'sale_order_invoice_partner',
    ],
}
