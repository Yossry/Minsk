
{
    'name': 'HR Attendance Extensions',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': "Employee Shift Scheduling",
    'author': "Farooq Arif",
    'website': 'http://www.aarsol.com',
    'license': 'AGPL-3',
	'depends': [		
		'hr_attendance',
		'hr_ext',		
		'base_suspend_security',
	],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
    	'security/hr_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
     	
		'views/hr_attendance_view.xml',
		'views/hr_month_attendance_view.xml',
		'views/hr_public_holidays_view.xml',
		'views/hr_holidays_view.xml',
		'views/dashboard_views.xml',
		
		'wizard/validate_holidays_view.xml',    
        'wizard/daily_attendance_wizard_view.xml',
        'wizard/attendance_wizard_view.xml',
        'wizard/leaves_report_wizard_view.xml',

		'report/report.xml',
        'report/report_dailyattendance.xml',
        'report/report_attendance.xml',
        #'report/report_annual_attendance.xml',
      	'menu/menu.xml',
      	
    ],
    'test': [
    ],
    'qweb': ['static/src/xml/dashboard.xml'],
    'installable': True,
	'application': True,
}
