{
    'name': 'SOS Reports',
    'version': '0.1',
    'category': 'SOS',
    'license': 'AGPL-3',
    'description': "This module provides various Reports for SOS",
    'author': 'Farooq',
    'website': 'http://www.aarsolerp.com/',
    'depends': ['sos','sos_payroll'],
    'init_xml': [],
    'data': [
    	#***** Wizards *****#
    	#*******************#
    	
    	#Directory:- Attendance
    	'wizard/attendance/attendance_invoice_comp_view.xml',
    	'wizard/attendance/biometric_attendance_wizard_view.xml',
    	'wizard/attendance/biometric_attendance_summary_wizard_view.xml',
    	'wizard/attendance/biometric_excel_attendance_view.xml',
    	
    	#Directory:- Invoices
    	'wizard/invoices/invoices_status_report_view.xml',
    	'wizard/invoices/invoices_comp_summary_view.xml',
    	'wizard/invoices/invoices_verification_view.xml',
    	
    	
    	#Directory:- General
    	#'wizard/general/sos_guards_working_detail_wizard_view.xml',
    	#'wizard/general/bankcharges_summary_view.xml',
    	'wizard/general/gst_summary_view.xml',
    	#'wizard/general/payslip_summary_view.xml',
    	#'wizard/general/profitability_summary_view.xml',
		#'wizard/general/report_post_ledger_view.xml',
    	
    	#Directory:- Salary
    	'wizard/salary/salary_invoice_comp_view.xml',
    	#'wizard/salary/guards_salary_expense_view.xml',
    	#'wizard/salary/salary_comp_summary_view.xml',
    	
    	#Directory:- Recovery
    	#'wizard/recovery/pending_recovery_wizard_view.xml',

		#Directory:- Taxes
		'wizard/taxes/tax_at_source_wiz_view.xml',
		
		#***** Reports *****#
		#*******************#
		
		#Directory:- Attendance
		'report/attendance/report_attendance_invoicecomp.xml',
		#'report/attendance/report_biometricattendance.xml',
		'report/attendance/report_biometric_attendancesummary.xml',
		'report/attendance/report_guard_biometricattendance.xml',
			
		#Directory:- Invoices
		'report/invoices/report_invoice_centerstatus.xml',
		'report/invoices/report_invoice_poststatus.xml',
		'report/invoices/report_invoice_projectstatus.xml',
		'report/invoices/report_invoice_compsummaryproject.xml',
		'report/invoices/report_invoice_compsummarycenter.xml',
		'report/invoices/report_invoice_compsummarypost.xml',
		'report/invoices/report_invoices_verification.xml',
		
		#Directory:- General
		'report/general/report_gst_summaryproject.xml',
		'report/general/report_gst_summarycenter.xml',
    	'report/general/report_gst_summarypost.xml',
    	'report/general/report_gst_summarypercentage.xml',
    	#'report/general/report_post_ledger.xml',
		#'report/general/report_profitability_summarycenter.xml',
		#'report/general/report_profitability_summarycenterproject.xml',
		#'report/general/report_profitability_summaryproject.xml',
    	#'report/general/report_profitability_summaryprojectcenter.xml',
    	#'report/general/report_common_summarycenter.xml',
    	#'report/general/report_common_summarypost.xml',
		#'report/general/report_common_summaryproject.xml',
		
		#Directory:- Salary
		'report/salary/report_salary_invoicecomp.xml',
    	#'report/salary/report_guards_salary_projectwise.xml',
    	#'report/salary/report_guards_salary_regionwise.xml',
    	#'report/salary/report_compsummarycenter.xml',
		#'report/salary/report_compsummarypost.xml',
		#'report/salary/report_compsummaryproject.xml',
		
		#Directory:- Recovery
    	#'report/new_reports/project_report_pendingrecovery.xml',
    	#'report/new_reports/center_report_pendingrecovery.xml',
    	#'report/new_reports/post_report_pendingrecovery.xml',
    	#'report/new_reports/guards_working_detail_report.xml',

		#Directory:- Taxes
		'report/taxes/tax_at_source_report.xml',


       	'report/attendance/report.xml',
       	'report/general/report.xml',
       	'report/invoices/report.xml',
       	#'report/recovery/report.xml',
       	'report/salary/report.xml',
		'report/taxes/report.xml',

        'menu/sos_report_menu.xml',
        
    ],
    'demo_xml': [],
    
    'installable': True,
    'application' : True,
}


