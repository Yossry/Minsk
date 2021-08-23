{
    'name': 'AARSOL Common Extensions',
    'version': '12.0',
    'category': 'Account',
    "description": """ AARSOL Common Extensions """,
    'author': "Muhammad Farooq Arif <farooq@aarsol.com>",
    'website': 'http://www.aarsolerp.pk/',
    'license': 'AGPL-3',	
    'depends': [
		'base','account',      
    ], #'accounting_pdf_reports',
    'data': [
		'security/ir.model.access.csv',
				
		'views/aarsol_view.xml',
		'views/accounts_view.xml',
		
		#'views/zebra_printer_view.xml',
        #'views/res_company_view.xml',
        
        #'wizard/report_wizards_view.xml',
		#'wizard/partner_statement_view.xml',
		#'wizard/employee_statement_view.xml',		
		#'wizard/trail_rep_wizard.xml',
		#'report/report.xml',
		
		#'report/partner_statement.xml',
		#'report/employee_statement.xml',
		#'report/trial_balance.xml',
		
	
		#'report/payment/reports.xml',
		#'report/payment/res_company_view.xml',
		#'report/payment/account_payment_view.xml',
		#'report/payment/aarsol_payment_template.xml',
		#'report/payment/payment_data.xml',

    ],    
    'installable': True,
	'application': True,
	'qweb': [
        "static/src/xml/report.xml",
    ],
    
}
