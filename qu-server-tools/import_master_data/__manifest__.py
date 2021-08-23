# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Import Master Data",
    "summary": "Import master data files and download them as .xml",
    "version": "12.0.2.0.1",
    "category": "Import",
    "website": "https://www.qubiq.es",
    "author": "QubiQ",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        # Add the modules that creates the models to import
    ],

    "data": [
        "wizards/import_master_data.xml",
    ],
}
