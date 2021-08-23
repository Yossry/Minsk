# -*- coding: utf-8 -*-
import re

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

alphabet = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
    ('G', 'G'),
    ('H', 'H'),
    ('I', 'I'),
    ('J', 'J'),
    ('K', 'K'),
    ('L', 'L'),
    ('M', 'M'),
    ('N', 'N'),
    ('Ñ', 'Ñ'),
    ('O', 'O'),
    ('P', 'P'),
    ('Q', 'Q'),
    ('R', 'R'),
    ('S', 'S'),
    ('T', 'T'),
    ('U', 'U'),
    ('V', 'V'),
    ('W', 'W'),
    ('X', 'X'),
    ('Y', 'Y'),
    ('Z', 'Z')
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    field_1 = fields.Many2one('address.code', required=True)
    field_2 = fields.Integer(required=True)
    field_3 = fields.Selection(alphabet)
    field_4 = fields.Many2one('street.code')
    field_5 = fields.Integer(required=True)
    field_6 = fields.Selection(alphabet)
    field_7 = fields.Many2one('street.code')
    field_8 = fields.Integer(required=True)
    field_9 = fields.Many2one('address.code')
    field_10 = fields.Integer()
    field_11 = fields.Many2one('address.code')
    field_12 = fields.Integer()
    street = fields.Char()
    name = fields.Char(default=lambda self:self.first_name)
    first_name = fields.Char()
    middle_name = fields.Char()
    last_name = fields.Char()
    second_last_name = fields.Char()
    nit = fields.Char(string='NIT', size=11)
    dv = fields.Selection(
        [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
         ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')],
        string='DV')
    company_name = fields.Char()
    company_nature = fields.Selection(
        [('S.A.S', 'S.A.S'),
         ('S.A', 'S.A'),
         ('LTDA', 'LTDA'),
         ('PERSONA NATURAL', 'PERSONA NATURAL'),
         ('EMPRESA UNIPERSONAL', 'EMPRESA UNIPERSONAL'),
         ('SOCIEDAD COLECTIVA', 'SOCIEDAD COLECTIVA'),
         ('S. EN C.', 'S. EN C.'),
         ('S.C.A', 'S.C.A')])
    ciiu = fields.Many2many(
        'ciiu.value', 'ciiu_value_res_partner_rel', 'partner_id', 'ciiu_id',
        string='CIIU')

    _sql_constraints = [
        ('nit_partner_uniq', 'unique(nit)', 'NIT must be unique!'),
    ]

    @api.constrains('nit')
    def _check_nit_size(self):
        pattern = "^\+?[0-9]*$"
        for record in self:
            if record.nit and re.match(pattern, record.nit) is None:
                raise ValidationError(_("NIT value must be a numerical."))
    
    @api.onchange('nit','dv')
    def onchange_Concatenar_(self):
        self.vat ="%s%s" % (
            self.nit,
            self.dv)                        

    @api.onchange('l10n_co_edi_large_taxpayer')
    def _onchange_gran_contrib(self):
        if self.l10n_co_edi_large_taxpayer:
            self.l10n_co_edi_simplified_regimen = False

    @api.onchange('l10n_co_edi_simplified_regimen')
    def _onchange_simplified_reg(self):
        if self.l10n_co_edi_simplified_regimen:
            self.l10n_co_edi_large_taxpayer = False

    @api.onchange('field_1', 'field_2', 'field_3', 'field_4', 'field_5',
                  'field_6', 'field_7', 'field_8', 'field_9', 'field_10',
                  'field_11', 'field_12')
    def _onchange_street(self):
        self.street = "%s %s  %s %s %s %s %s %s %s %s %s %s" % (
            self.field_1.code if self.field_1 else "",
            str(self.field_2),
            str(self.field_3 if self.field_3 else ""),
            self.field_4.code if self.field_4 else "",
            str(self.field_5),
            str(self.field_6 if self.field_6 else ""),
            self.field_7.code if self.field_7 else "",
            str(self.field_8),
            self.field_9.code if self.field_9 else "",
            str(self.field_10),
            self.field_11.code if self.field_11 else "",
            str(self.field_12))

    @api.onchange('first_name', 'middle_name', 'last_name', 'second_last_name', 'company_name', 'company_nature')
    def _onchange_full_name(self):
        if self.company_type == 'person':
            self.name = "%s %s %s %s" % (
                self.first_name if self.first_name else "",
                self.middle_name if self.middle_name else "",
                self.last_name if self.last_name else "",
                self.second_last_name if self.second_last_name else "")
        else:
            self.name = "%s %s" % (
                self.company_name if self.company_name else "",
                self.company_nature if self.company_nature else "")
