# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Company logo visibility",
    "category": "Security",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Quartile Limited",
    "website": "https://www.quartile.co",
    "depends": ["falcon_material_backend_theme"],
    "summary": """""",
    "data": [
        "security/res_groups.xml",
        "views/base_company_logo_visibility_templates.xml",
    ],
    "qweb": ["static/src/xml/new_menu.xml"],
    "installable": True,
}
