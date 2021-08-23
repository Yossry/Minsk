# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name':'SDi-CRM: Sync activity with meeting',
    "version": "12.0.1.0.1",
    'category': "Uncategorized",
    'author':'David Juaneda',
    'summary': """
        Sync activitiy with meetings.""",
    'description': """
This is a full-featured crm system.
========================================

It supports:
------------

    Complete the title of the meetings with information from the opportunity or from the client.

    """,
    'license':'AGPL-3',
    'depends':[
        'crm',
        'mail',
        'activities_done'
    ],
    'data':[
        'views/activities_sync_event_templates.xml',
    ],
    'installable': True,
}
