# -*- coding: utf-8 -*-
{
    'name': "Logistics Management",
    'summary': """
        Logistic management system developed based on odoo 12 enterprise, it helps logistics companies 
        to manage their shipments and documentation.""",

    'description': """
        Logistic module developed based on odoo 12 enterprise, it helps logistics companies 
        to manage their shipments and documentations.
    """,

    'author': "Codesk Company",
    'website': "http:www.codesk.systems",

    'category': 'Uncategorized',
    'version': '12.0.1.0',
    'depends': ['base','mail','hr_attendance','contacts','sale','base_address_city','product','hr','documents','account','base_address_city','hr_attendance','helpdesk','base_address_extended'],

    'data': [
       'security/ir.model.access.csv',
       'views/views.xml',
#        'report/sale_inquiry_report.xml',
       'views/container_size_view.xml',
       'views/agreement_method_view.xml',
       'views/custoemr_class_view.xml',
#        'report/sale_report.xml',
       'views/customs_declaration_view.xml',
       'views/insurance_type_view.xml',
       'views/insurance_items.xml',
       'views/truck_type_view.xml',
       'views/weight_type_view.xml',
       'views/vessel_views.xml',
       'views/place_view.xml',
       'views/transport_type_view.xml',
       'views/line_cost_views.xml',
#        'views/loading_place_view.xml',
       'views/insurance_cost_view.xml',
       'views/transport_cost_view.xml',
       'views/clearance_cost_view.xml',
       'views/air_line_cost.xml',
       'views/sale_inquiry.xml',
       'data/data.xml',
       'views/invoice_charges.xml',
       'views/commodity.xml',
       'views/packaging_views.xml',
       'views/job_views.xml',
#        'views/driver_line.xml',
       'views/bill_of_lading.xml',
       'views/external_bill_of_lading.xml',
       'views/route.xml',
       'views/job_position.xml',
       'views/dhl_logistic_views.xml',
       'views/menus_views.xml',  
       'security/security.xml'    
    ],
}
