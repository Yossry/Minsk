# Copyright 2018 Thinkwell Designs <dave@thinkwelldesigns.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Add interest charges to overdue invoices.',
    'summary': 'Add interest charges to overdue invoices.',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Thinkwell Designs',
    'website': 'https://github.com/thinkwelltwd/countinghouse',
    'category': 'Banking addons',
    'depends': [
        'account',
        'account_cancel',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/account_payment_term.xml',
        'data/charge_interest_cron.xml',
    ],
    'post_init_hook': 'set_charge_date',
    'installable': True,
}
