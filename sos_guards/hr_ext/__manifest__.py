
{
    'name': 'HR Extensions',
    'version': '8.0',
    'category': 'Human Resources',
    'author': "Muhammad Farooq Arif <farooq@aarsol.com>",
    'website': 'http://edu.aarsolerp.pk/',
    'license': 'AGPL-3',
	'description': """
Make Employee Records and Contracts Easier to Work With
=======================================================
    1. Make the job id in employee object reference job id in latest contract.
    2. When moving from employee to contract pre-populate the employee field.
    3. In the contract form show only those positions belonging to the
       department the employee belongs to.
    4. Make country (nationality) default to Ethiopia
    5. Make official identification document number unique

Define Initial Settings on New Contracts
========================================
    - Starting Wages
    - Salary Structure
    - Trial Period Length

Employee Contract Workflow and Notifications
============================================

Easily find and keep track of employees who are nearing the end of their
contracts and trial periods.

Employee's Employment Status
============================

Track the HR status of employees.

HR Policy Groups
================

Define a collection of policies, such as Overtime, that apply to a contract.

Define Absence Policies
========================
Define properties of an absence policy, such as:
    * Type (paid, unpaid)
    * Rate (multiplier of base wage)

Define Overtime Policies
========================
Define properties of an overtime policy, such as:
    * Type (daily, weekly, or holiday)
    * Rate (multiplier of base wage)
    * Active Hours

    """,
    'depends': [
    	'base',
    	'base_suspend_security',
		'hr',		
        'hr_contract',        		
        'hr_payroll',
        'hr_holidays',			
    ],
    'data': [
		'security/hr_security.xml',
		'security/ir.model.access.csv',
		'security/ir_rule.xml', 
		
		'data/birth_template_data.xml',

        'views/hr_job_view.xml',
		'views/hr_contract_template_view.xml',		
        'views/hr_contract_view.xml',

		'views/hr_employee_view.xml',
		'views/hr_employee_termination_view.xml',

		'views/hr_document_expiry_view.xml',
		'views/hr_health_insurrance_view.xml',
		
		'views/hr_policy_group_view.xml',
		'views/hr_policy_absence_view.xml',
		'views/hr_policy_ot_view.xml',
		'views/hr_view.xml',
						
		#'cron/hr_ext_cron.xml',
               
        'wizard/end_contract_view.xml',
        'wizard/employee_profile_wizard_view.xml',
		'wizard/employee_contract_wizard_view.xml',
		'wizard/expire_docs_wizard_view.xml',
		
        'report/report_employee_profile.xml',
		'report/report_employee_contract.xml',
		'report/report_expire_docs.xml',
		
		'report/report.xml',      
		'menus/menu.xml',
		
    ],
    'test': [],    
    'installable': True,
	'application': True,
}
