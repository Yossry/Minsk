# Copyright 2019 Xavier Jimenez <xavier.jimenez@qubiq.es>
# Copyright 2019 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Webservice Integration',
    'summary': 'Webservice Integration',
    'version': '13.0.1.0.0',
    'category': 'Account',
    'author': 'QubiQ',
    'website': 'https://www.qubiq.es',
    'depends': [
        'queue_job',
    ],
    "data": [
        "security/security.xml",
        "views/menu.xml",
        "views/webservice_instance_view.xml",
        "views/webservice_mapper_view.xml",
        "wizards/export_mappers.xml",
        "wizards/import_mappers.xml",
    ],
    'application': True,
    'installable': True,
}
