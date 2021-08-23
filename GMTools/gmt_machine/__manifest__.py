# See LICENSE file for full copyright and licensing details.

{
    'name': "GMT Tools",
    'version': '12.0.1.0.0',
    'summary': """
        A system to retain data of gmt machines""",
    'description': """
        A system to retain data of GMT machines
    """,
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'website': "http://www.serpentcs.com",
    'category': 'product',
    'license': 'AGPL-3',
    'depends': ['product'],
    'data': [
          'security/security_view.xml',
          'security/ir.model.access.csv',
          'views/activity_log_view.xml',
          'views/overall_equipment_effectiveness_view.xml',
          'views/quality_control_view.xml',
          'views/machine_view.xml',
          'views/machine_image_view.xml',
             ],
    'installable': True,
    'application': True,

}
