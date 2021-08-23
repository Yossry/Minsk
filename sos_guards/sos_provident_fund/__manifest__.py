
{
    'name': 'SOS Provident Fund Reports',
    'version': '0.1',
    'category': 'SOS',
    'license': 'AGPL-3',
    'description': "This module provides various Reports for Guards As well as Staff Provident Fund Reports",
    'author': 'Farooq',
    'website': 'http://www.aarsolerp.com/',
    'depends': ['sos','sos_payroll'],
    'init_xml': [],
    'data': [
        'data/sos_data.xml',
        'security/ir.model.access.csv',
		'security/sos_security.xml',

    	'wizard/pf_employee_contribution_wizard_view.xml',
		'wizard/pf_employer_contribution_wizard_view.xml',
		'wizard/pf_employee_statement_wizard_view.xml',
        'wizard/terminated_guards_3x_interval_pf_wizard_view.xml',
        'wizard/month_wise_pf_wizard_view.xml',
		
		'report/report_pf_employeecontribution.xml',
		'report/report_pf_employercontribution.xml',
		'report/report_pf_employeestatement.xml',
        'report/terminated_guards_3x_interval_pf_report.xml',
        'report/month_wise_pf_report.xml',
		
		'views/purchase_order_ext_view.xml',
        'views/guards_pf_return_form_view.xml',
    	
        'report/report.xml',
        'menu/sos_provident_fund_menu.xml',
        
    ],
    'demo_xml': [],
    
    'installable': True,
    'application' : True,
}


