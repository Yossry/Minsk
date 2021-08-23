{
    'name': 'Theme Artesia',
    'category': 'Theme/Creative',
    'version': '12.0',
    'license': 'LGPL-3',
    'author': 'Key Concepts',
    'website': 'http://keyconcepts.co.in',
    'depends': ['website', 'crm'],
    'summary': "Artesia Website",
    'description': """
        Theme Artesia.
        - Use finely designed building blocks and edit everything inline. 
        - Super Clean Snippets.
        - Fully and Easy Customizable
        - Responsive content on all pages.
        - Selection of color
        - 4 Different style homepage
        - Edit Anything Inline.
        """,
    'data': [
            "security/ir.model.access.csv",
            "views/website_subscribe_view.xml",
            "views/template.xml",
            "views/snippets.xml",
            #'views/signup_modal.xml',
    ],
    "sequence": 1,
    'installable': True,
    'application':True,
    'price': 109,
    'currency': "EUR",
    'images': [
            'static/description/artesia_business_poster.jpg',
            'static/description/artesia_business_screenshot.jpg',
            ],
    'live_test_url': 'http://artesia.kcits.co.in/',
}   
