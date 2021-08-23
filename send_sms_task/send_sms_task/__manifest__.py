# -*- coding: utf-8 -*-
{
    'name': "send_sms_task",

    'summary': """
        send SMS notification to user linked with project task""",

    'description': """
Send task name to the employee by sms (twilio gateway)  
follow instraction from the following vedio
https://www.facebook.com/yasr3mr96/videos/202191610789649/ 
 you must install  twilio on ubuntu by the following command
 
 pip3 install twilio
""",

    'author': "yasser Omer",
    'website': "https://www.facebook.com/yasr3mr96",
    'phone':'01028408177',
    'email': 'yasr3mr796@gmail.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project'],

    # always loaded
    'data': [
        'views/views.xml',
        'wizards/wizard_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
