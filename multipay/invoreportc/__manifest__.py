{
    'name': "C. Invoice Report",

    'summary': """
        Custom invoice report""",

    'description': """
        Custom invoice report 
    """,
    'author': "SmartDoo",
    'website': "http://www.smartdoo.com",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base',],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}