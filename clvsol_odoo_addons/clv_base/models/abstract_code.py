# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


def format_code(code_seq):
    code = list(map(int, str(code_seq)))
    code_len = len(code)
    while len(code) < 14:
        code.insert(0, 0)
    while len(code) < 16:
        n = sum([(len(code) + 1 - i) * v for i, v in enumerate(code)]) % 11
        if n > 1:
            f = 11 - n
        else:
            f = 0
        code.append(f)
    code_str = "%s.%s.%s.%s.%s-%s" % (str(code[0]) + str(code[1]),
                                      str(code[2]) + str(code[3]) + str(code[4]),
                                      str(code[5]) + str(code[6]) + str(code[7]),
                                      str(code[8]) + str(code[9]) + str(code[10]),
                                      str(code[11]) + str(code[12]) + str(code[13]),
                                      str(code[14]) + str(code[15]))
    if code_len <= 3:
        code_form = code_str[18 - code_len:21]
    elif code_len > 3 and code_len <= 6:
        code_form = code_str[17 - code_len:21]
    elif code_len > 6 and code_len <= 9:
        code_form = code_str[16 - code_len:21]
    elif code_len > 9 and code_len <= 12:
        code_form = code_str[15 - code_len:21]
    elif code_len > 12 and code_len <= 14:
        code_form = code_str[14 - code_len:21]
    return code_form


class AbstractCode(models.AbstractModel):
    _description = 'Abstract Code'
    _name = 'clv.abstract.code'

    code = fields.Char(
        string='Code', required=False, default=False,
        help='Use "/" to get an automatic new Code.'
    )
    code_sequence = fields.Char(string='Code Sequence', required=False, default=False)

    @api.model
    def create(self, values):
        if 'code_sequence' in values:
            if 'code' not in values or ('code' in values and values['code'] == '/'):
                code_seq = self.env['ir.sequence'].next_by_code(values['code_sequence'])
                values['code'] = format_code(code_seq)
        else:
            if 'code' not in values or ('code' in values and values['code'] == '/'):
                values['code'] = False
        return super().create(values)

    @api.multi
    def write(self, values):
        if 'code_sequence' not in values:
            if 'code' in values and values['code'] == '/':
                code_seq = self.env['ir.sequence'].next_by_code(self.code_sequence)
                values['code'] = format_code(code_seq)
        return super().write(values)

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'code': '/', })
        return super().copy(default)
