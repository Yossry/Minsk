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


class ResPartnerWizard(models.TransientModel):
    _name = 'res.partner.wizard'
    _description = 'Wizard for Res Partner'

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

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    is_company = fields.Boolean(string='Is a Company',
                                help="Check if the contact is a company, otherwise it is a person")
    company_type = fields.Selection([('person', 'Individual'),
                                     ('company', 'Company')],
                                    string='Company Type')
    name = fields.Char()
    first_name = fields.Char()
    middle_name = fields.Char()
    last_name = fields.Char()
    second_last_name = fields.Char()
    street = fields.Char()
    city = fields.Char()
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
    ciiu = fields.Many2many('ciiu.value', string='CIIU')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    state_id = fields.Many2one('res.country.state', string='State', ondelete='restrict')
    zip = fields.Char('ZIP')

    l10n_co_document_type = fields.Selection(
        [('rut', 'RUT'),
         ('id_document', 'Cédula'),
         ('id_card', 'Tarjeta de Identidad'),
         ('passport', 'Pasaporte'),
         ('foreign_id_card', 'Cédula Extranjera'),
         ('external_id', 'ID del Exterior'),
         ('diplomatic_card', 'Carné Diplomatico'),
         ('residence_document', 'Salvoconducto de Permanencia'),
         ('civil_registration', 'Registro Civil'),
         ('national_citizen_id', 'Cédula de ciudadanía')],
        string='Document Type',
        help='Indicates to what document the information in here belongs to.')
    nit = fields.Char(string='NIT', size=9, required=True)
    dv = fields.Selection(
        [('', ''), ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
         ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')],
        string='DV')  # for some reason, if required is applied in form, there is not displayed empty option, that's why it is added here
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    l10n_co_edi_obligation_type_ids = fields.Many2many(
        'l10n_co_edi.type_code', string='Obligaciones y Responsabilidades',
        domain=[('type', '=', 'obligation')])
    l10n_co_edi_large_taxpayer = fields.Boolean('Gran Contribuyente')
    l10n_co_edi_simplified_regimen = fields.Boolean('Simplified Regimen')
    ciiu = fields.Many2many(
        'ciiu.value', string='CIIU')
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

    @api.constrains('nit')
    def _check_nit_size(self):
        pattern = "^\+?[0-9]*$"
        for record in self:
            if re.match(pattern, record.nit) is None:
                raise ValidationError(_("NIT value must be a numerical."))

    @api.onchange('l10n_co_edi_large_taxpayer')
    def _onchange_gran_contrib(self):
        if self.l10n_co_edi_large_taxpayer:
            self.l10n_co_edi_simplified_regimen = False

    @api.onchange('l10n_co_edi_simplified_regimen')
    def _onchange_simplified_reg(self):
        if self.l10n_co_edi_simplified_regimen:
            self.l10n_co_edi_large_taxpayer = False

    @api.multi
    def action_save(self):
        if not self.l10n_co_edi_large_taxpayer and not self.l10n_co_edi_simplified_regimen:
            raise ValidationError(_('Large taxpayer or Simplified Regimen must be selected'))
        self.partner_id.write({
            'name': self.name,
            'city': self.city,
            'street': self.street,
            'is_company': self.is_company,
            'company_type': self.company_type,
            'field_12': self.field_12,
            'field_11': self.field_11.id,
            'field_10': self.field_10,
            'field_9': self.field_9.id,
            'field_8': self.field_8,
            'field_7': self.field_7.id,
            'field_6': self.field_6,
            'field_5': self.field_5,
            'field_4': self.field_4.id,
            'field_3': self.field_3,
            'field_2': self.field_2,
            'field_1': self.field_1.id,
            'l10n_co_edi_simplified_regimen': self.l10n_co_edi_simplified_regimen,
            'l10n_co_edi_large_taxpayer': self.l10n_co_edi_large_taxpayer,
            'l10n_co_edi_obligation_type_ids': [
                (6, 0, self.l10n_co_edi_obligation_type_ids.ids)],
            'email': self.email,
            'mobile': self.mobile,
            'phone': self.phone,
            'nit': self.nit,
            'dv': self.dv,
            'zip': self.zip,
            'state_id': self.state_id.id,
            'l10n_co_document_type': self.l10n_co_document_type,
            'country_id': self.country_id.id,
            'company_nature': self.company_nature,
            'company_name': self.company_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'second_last_name': self.second_last_name,
            'ciiu': [(6, 0, self.ciiu.ids)]
        })

        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'purchase.order' and active_id:
            self.env['purchase.order'].browse(active_id).button_confirm()
        elif self._context.get('active_model') == 'sale.order' and active_id:
            self.env['sale.order'].browse(active_id).action_confirm()

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

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.state_id = False
        if self.country_id:
            return {'domain': {
                'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}
