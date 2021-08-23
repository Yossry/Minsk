{
    'name': 'AARSOL Accounts Extensions',
    'version': '12.0',
    'category': 'Account',
    "description": """ AARSOL Accounts Management """,
    'author': "Muhammad Farooq Arif <farooq@aarsol.com>",
    'website': 'http://www.aarsolerp.pk/',
    'license': 'AGPL-3',	
    'depends': [
		'base','account','analytic_structure','aarsol_common','professional_templates',      
    ],
    'data': [
		'security/ir.model.access.csv',
		
		#'views/account_template.xml',
        'views/accounts_view.xml',
        'views/dimensions_view.xml',

		#'wizard/report_wizards_view.xml',		
		'wizard/dimensions_view.xml',
        'wizard/aarsol_general_ledger_view.xml',
		#'wizard/ledger_summary_view.xml',
     		
		'report/aarsol_general_ledger.xml',
		#'report/ledger_summary.xml',

		'report/journal_entry/reports.xml',
		'report/journal_entry/aarsol_jv_template.xml',
		'report/journal_entry/journal_data.xml',
		
#		'report/journal_entry/res_company_view.xml',
#		'report/journal_entry/account_journal_entry_view.xml',

		#'report/payment/reports.xml',
		#'report/payment/res_company_view.xml',
		#'report/payment/account_payment_view.xml',
		#'report/payment/aarsol_payment_template.xml',
		#'report/payment/payment_data.xml',
    ],
    'installable': True,
	'application': True,
}

