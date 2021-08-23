from odoo import http
from odoo.exceptions import UserError

FILE_NAME = 'export_bank.csv'


class Controller(http.Controller):

    @http.route('/treasury/forecast/download/<int:rec_id>', auth='user', type='http')
    def export_table(self, rec_id, **kw):
        import pandas as pd

        BankBalance = http.request.env['bank.balance.computation']

        balance_id = BankBalance.browse(rec_id)

        if not balance_id:
            raise UserError('Record for {} model could not be found.'.format(BankBalance))

        csv_file = None
        for i, df in enumerate(pd.read_html(
                balance_id.bank_balances, encoding='utf-8')):

            csv_file = df.to_csv(encoding='utf-8')

        if not csv_file:
            raise UserError('Issue creating csv file for bank balance {}.'.format(
                rec_id
            ))

        return http.request.make_response(csv_file, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', http.content_disposition(FILE_NAME)),
        ])
