{
	'name': 'Complaint Management System for SOS',
	'version': '0.1',
	'category': 'Security Guards System',
	'license': 'AGPL-3',
	'description': "This module manages the Complaints at SOS",
	'author': 'Farooq',
	'website': 'http://www.aarsolerp.com/',
	'depends': ['hr','sos'],
	'init_xml': [],
	'data': [
		'sos_data.xml',
		'security/ir.model.access.csv',  
    	
		'views/complaint_view.xml',
		'views/inspection_view.xml',
		'views/post_deployment_view.xml',
		'views/post_termination_view.xml',
		'views/sos_additional_guard_proforma_view.xml',
		'views/sos_guard_incident_view.xml',
		'views/sos_guest_house_approval_view.xml',
		'views/sos_rent_car_approval_view.xml',
		'views/sos_reservation_approval_view.xml',
    	
		'report/report_complaintstatistics.xml',
		'report/report_complaintsummary.xml',
		'report/report_complaintdetail.xml',
		'report/report_additionalguard.xml',
		'report/report_air_travel_summary.xml',
		'report/report_guest_house_summary.xml',
		'report/report_rent_car_summary.xml',
		
		      
        
		'wizard/complaints_summary_view.xml',
		'wizard/complaints_statistics_project_view.xml',
		'wizard/additional_guard_report_view.xml',
		'wizard/air_travel_summary_wiz_view.xml',
		'wizard/guest_house_summary_wiz_view.xml',
		'wizard/rent_car_summary_wiz_view.xml',
		
		'report/report.xml',
		'menu/sos_complaint_menu.xml',       
        
        
	],
	'demo_xml': [],
	'installable': True,
	'application' : True,
}


