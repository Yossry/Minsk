{
    'name': 'HR Payroll Extensions',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
		Easy Payroll Management
		=======================
		This module implements a more formal payroll cycle.
		This cycle is based on payroll period schedules configured by the user.
		An end-of-pay-period wizard guides the HR officer or manager through
		the payroll process. For each payroll period a specific set
		of criteria have to be met in order to proceed to the next stage of the
		process. For example:
			- Attendance records are complete

		Payroll Register
		================
			- Process payslips by department

		Add Amendments to Current and Future Pay Slips
		==============================================
    """,
    'author': "Farooq Arif",
    'website': 'http://www.aarsol.com',
    'license': 'AGPL-3',
	'depends': [
		'hr_attendance_ext','wizard_planner',		
	],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [    	
        'security/ir.model.access.csv',
		'data/hr_payroll_period_data.xml',
		'data/payslip_template_data.xml',
		
      	'views/salary_planner.xml',   
      			
		'views/hr_payroll_view.xml',		
		'views/hr_payslip_amendment_view.xml',
		'views/hr_payroll_period_view.xml',
		'views/hr_payroll_register_view.xml',
		'views/hr_payroll_run_advice_view.xml',				
		'views/hr_contract_view.xml',

		'views/loan_view.xml',
		'views/hr_staff_advance_view.xml',
		'views/hr_salary_inputs_view.xml',
		
		'views/attendance_variation_view.xml',
		'views/hr_staff_salary_difference_view.xml', 	
				
		'wizard/hr_payroll_register_run_view.xml',	
		'wizard/wps_view.xml',
		'wizard/hr_contract_revise_view.xml',
		'wizard/salary_sheet_save_wizard_view.xml',
		'wizard/staff_payroll_advice_summary_view.xml',
		
		'wizard/multi_payslip_done_wizard_view.xml',		
		
        #'cron/hr_payroll_period_cron.xml',

		'report/report.xml',
		'report/report_salary_sheet.xml',
		'report/report_salary_accounts.xml',
		#'report/menu_payslip_report.xml',
		'report/report_payslip.xml',
		'report/report_payslip_details.xml',
		'report/payslip_email_template.xml',
		'report/payroll_advice_summary_report.xml',
		
      	'menu/menu.xml',
		
		#'wizard/hr_employee_promotion_wizard_view.xml',
		#'wizard/hr_salary_increment_wizard_view.xml',
		#'report/payroll_register/hr_payroll_register_report.xml',
		#'report/report_payslip.xml',
		#'report/report_payslipdetails.xml',
    ],
    'test': [
    ],
    'qweb': ['static/src/xml/wizard_planner.xml'],
    'installable': True,
	'application': True,
}

