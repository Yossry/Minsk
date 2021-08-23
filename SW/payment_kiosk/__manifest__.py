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
    'name': 'QPR Kiosk',
    'category': 'Payment Transaction',
    'version': '1.0',
    'description': """
QPR Kiosk Module
================
QPR Custom Build Module to Keep the record of all transactions processed in Kiosk Terminal.
Mapping each transaction with the right Terminal and performing the various Calculation it it,
based on the services and margin defined.

This module allows to pass entries to accounting module and generate Payable records to easy reconcile with the service
provider's payments.

    """,
    'sequence': 0,
    'depends': ['base', 'web', 'account'],
    'data': [
        'security/ir.model.access.csv',

        'views/views.xml',
        'views/kiosk_terminal_view.xml',
        'views/kiosk_payment_channel_view.xml',
        'views/kiosk_service_view.xml',
        'views/partner_view.xml',

        'wizard/kiosk_transaction_views.xml',

        'report/kiosk_transaction_report.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
