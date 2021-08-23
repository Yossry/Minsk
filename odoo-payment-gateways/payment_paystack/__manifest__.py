{
    "name": "Paystack Payment",
    "version": "1.0",
    "depends": ["payment", "account", "website_sale"],
    "author": "Mattobell",
    "website": "http://www.mattobell.com",
    "description": """
     Paystack Payment
    """,
    "category": "Hidden",
    "data": [
        "views/paystack.xml",
        # 'views/config_setting_view.xml',
        "views/paystack_payment_transaction.xml",
        "data/paystack_acquire_data.xml",
    ],
    "installable": True,
}
