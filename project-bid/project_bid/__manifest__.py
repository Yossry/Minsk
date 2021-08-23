# Copyright 2015-19 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Project Bid",
    "version": "12.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L.",
    "website": "www.eficent.com",
    "license": "LGPL-3",
    "category": "Generic Modules/Projects & Services",
    "depends": ["project", "product"],
    "data": [
        "security/project_bid_security.xml",
        "view/project_bid_template_view.xml",
        "view/project_bid_view.xml",
        "security/ir.model.access.csv",
        "data/project_bid_data.xml",
    ],
    "installable": True,
}
