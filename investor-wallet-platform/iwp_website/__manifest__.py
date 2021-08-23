# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Investor Wallet Platform Website",
    'summary': """Website element for Investor Wallet Platform""",
    'version': '12.0.0.12.1',
    'license': 'AGPL-3',
    'author': "Coop IT Easy SCRLfs",
    'website': "https://coopiteasy.be",
    'depends': [
        'auth_signup',
        'portal',
        'investor_wallet_platform_base',
    ],
    'data': [
        'templates/assets.xml',
        'templates/showcase_website_links.xml',
        'templates/form.xml',
        'templates/auth_signup_form.xml',
        'templates/portal_my_wallet.xml',
        'templates/investor_portal_form.xml',
        'templates/subscription_request_form.xml',
        'templates/operation_request.xml',
        'templates/loan_issue_form.xml',
        'templates/manual_share_form.xml',
        'templates/manual_loan_form.xml',
    ],
    'demo': [
        'demo/users.xml',
    ],
}
