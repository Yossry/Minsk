{
	'name': 'SOS Accounts Inheritance',
	'version': '0.1',
	'category': 'Security Guards System',
	'license': 'AGPL-3',
	'description': "This module Inherits the Accounting Behaviors for SOS",
	'author': 'Muhammad Farooq Arif',
	'website': 'http://www.aarsolerp.com/',
	'depends': ['account','account_asset','asset','sos'],
	'init_xml': [],
	'data': [
		'security/account_security.xml',
		'security/ir.model.access.csv',        
		'data/account_data.xml',

		'views/sos_invoice_view.xml',
		'views/sos_accounts_cron.xml',
		'views/sos_accounts_view.xml',
		'views/invoices_cron_view.xml',
		'views/sos_abl_incentive_view.xml',
		'views/account_checkbook_view.xml',   
		'views/assets.xml',
		
		'wizard/invoice_states_view.xml',  
		'wizard/invoices_cron_wizard_view.xml',
		'wizard/invoices_debit_note_wizard_view.xml',
		'wizard/invoice_draft_wizard_view.xml',

		'report/report.xml',
		'report/report_sale_invoice.xml',
		'report/report_sos_cashbook.xml',
        
    ],
    'demo_xml': [],
    'installable': True,
    'application' : True,
}


