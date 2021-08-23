# -*- coding: utf-8 -*-
{
	'name': 'Import Sale Order from Excel or CSV File',
	'version': '11.0.0.0',
	'sequence': 4,
	'summary': 'Easy to Import multiple sales order with multiple sales order lines on Odoo by Using CSV/XLS file',
	'category': 'Sales',
	"currency": 'EUR',
	'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module use for import bulk Sales from Excel file. Import Sale order lines from CSV or Excel file.
	Import Sale, Import Sale order line, Import Sales, Import SO. Sale Import, Add SO from Excel.Add Excel Sale order.Add CSV file.Import Sale data. Import excel file
	-
	""",
	'author': 'BrowseInfo',
	'website': '',
	'depends': ['base','sos'],
	'data': [
		"bills.xml",
		"sos_accounts_updation.xml"	
		     ],
	'qweb': [
		],
	'demo': [],
	'test': [],
	'installable': True,
	'auto_install': False,
	"images":['static/description/Banner.png'],
}
