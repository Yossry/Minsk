# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    """
    Function inherited to do the account_move_line checking
    when the account_move is posted
    """
    @api.multi
    def post(self, invoice=False):
        for move in self:
            move.assert_balanced(force=True)
        return super(AccountMove, self).post(invoice=invoice)

    """
    Function overrited, otherwise you can't change amounts
    when importing account_move_lines.
    """
    @api.multi
    def assert_balanced(self, force=False):
        for s in self:
            if s.state != 'draft' or force:
                if not s.ids:
                    return True
                prec = s.env['decimal.precision'].precision_get('Account')

                s._cr.execute("""\
                    SELECT      move_id
                    FROM        account_move_line
                    WHERE       move_id in %s
                    GROUP BY    move_id
                    HAVING      abs(sum(debit) - sum(credit)) > %s
                    """, (tuple(s.ids), 10 ** (-max(5, prec))))
                if len(s._cr.fetchall()) != 0:
                    raise UserError(_(
                        "Cannot create unbalanced journal entry."))
        return True
