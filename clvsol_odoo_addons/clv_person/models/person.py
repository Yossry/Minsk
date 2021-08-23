# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.modules import get_module_resource
from odoo.exceptions import UserError

'''
    https://www.odoo.com/documentation/12.0/howtos/backend.html#internationalization
    https://www.odoo.com/documentation/12.0/reference/translations.html#explicit-exports
    https://books.google.com.br/books?id=4NRJDwAAQBAJ&pg=PA157&lpg=PA157&dq=%22odoo._()%22&source=bl&ots=oj2brUczLL&sig=ACfU3U2yvd8R9AOfAXyhe-NwrLikOp7bYQ&hl=pt-BR&sa=X&ved=2ahUKEwiNi8CAxs_gAhW1IrkGHc8KASQQ6AEwBXoECAgQAQ#v=onepage&q=%22odoo._()%22&f=false
    https://www.odoo.com/pt_BR/forum/help-1/question/what-is-the-meaning-of-the-underscore-in-the-python-odoo-import-statement-129061
'''


class Person(models.Model):

    _name = 'clv.person'
    _description = 'Person'
    _inherit = 'clv.abstract.partner_entity'

    @api.multi
    @api.depends('name', 'code', 'age_years')
    def name_get(self):
        result = []
        for record in self:
            if record.code and record.age_years:
                result.append(
                    (record.id,
                     u'%s [%s] (%s)' % (record.name, record.code, record.age_years)
                     ))
            else:
                if record.code:
                    result.append(
                        (record.id,
                         u'%s [%s]' % (record.name, record.code)
                         ))
                elif record.age_years:
                    result.append(
                        (record.id,
                         u'%s (%s)' % (record.name, record.age_years)
                         ))
                else:
                    result.append(
                        (record.id,
                         u'%s' % (record.name)
                         ))
        return result

    code = fields.Char(string='Person Code', required=False)

    notes = fields.Text(string='Notes:')

    estimated_age = fields.Char(string='Estimated Age', required=False)

    birthday = fields.Date(string="Date of Birth")
    age = fields.Char(
        string='Age',
        compute='_compute_age',
        # store=True
    )
    age_years = fields.Char(
        string="Age (years old)",
        compute='_compute_age',
        # store=True
    )
    # age_suport = fields.Char(
    #     string='Age Suport',
    #     compute='_compute_age_suport',
    #     store=False
    # )

    @api.multi
    @api.constrains('birthday')
    def _check_birthday(self):
        for person in self:
            if person.birthday:
                if person.birthday > fields.Date.today():
                    raise UserError(u'Date of Birth must be in the past!')

    @api.multi
    # @api.depends('birthday')
    def _compute_age(self):
        now = datetime.now()
        for r in self:
            if r.birthday:
                dob = datetime.strptime(str(r.birthday), '%Y-%m-%d')
                if r.is_deceased and bool(r.date_death):
                    dod = datetime.strptime(str(r.date_death), '%Y-%m-%d')
                    delta = relativedelta(dod, dob)
                    is_deceased = _(' (deceased)')
                elif r.is_deceased and not bool(r.date_death):
                    delta = relativedelta(now, dob)
                    is_deceased = _(' (deceased?)')
                else:
                    delta = relativedelta(now, dob)
                    is_deceased = ''
                years_months_days = '%d%s %d%s %d%s%s' % (
                    delta.years, _('y'), delta.months, _('m'), delta.days, _('d'),
                    is_deceased
                )
                years = '%d%s%s' % (
                    delta.years, _('y'),
                    is_deceased
                )
                r.age = years_months_days
                r.age_years = years
            else:
                r.age = "No Date of Birth!"
                r.age_years = False

    # @api.multi
    # def _compute_age_suport(self):
    #     now = datetime.now()
    #     for r in self:
    #         if r.birthday:
    #             dob = datetime.strptime(r.birthday, '%Y-%m-%d')
    #             delta = relativedelta(now, dob)
    #             # self.age = str(delta.years) + "y " + str(delta.months) + "m " + str(delta.days) + "d"
    #             age = str(delta.years)
    #         else:
    #             age = "No Date of Birth!"

    #         r.age_suport = age
    #         if r.age != age:
    #             record = self.env['clv.person'].search([('id', '=', r.id)])
    #             record.write({'birthday': r.birthday})

    date_reference = fields.Date(
        string="Reference Date",
        compute='_compute_date_reference',
        # store=True
    )
    age_reference = fields.Char(
        string='Reference Age',
        compute='_compute_age_reference',
        store=True
    )
    age_reference_years = fields.Char(
        string="Reference Age (years old)",
        compute='_compute_age_reference',
        store=True
    )
    # age_reference_suport = fields.Char(
    #     string='Reference Age Suport',
    #     compute='_compute_age_reference_suport',
    #     store=False
    # )

    @api.multi
    def _compute_date_reference(self):
        for r in self:
            date_reference = self.env['ir.config_parameter'].sudo().get_param(
                'clv.global_settings.current_date_reference', '').strip()
            r.date_reference = date_reference

    @api.multi
    @api.depends('date_reference', 'birthday', 'force_is_deceased', 'date_death')
    def _compute_age_reference(self):
        # for r in self:
        #     if r.date_reference:
        #         if r.birthday:
        #             dob = datetime.strptime(r.birthday, '%Y-%m-%d')
        #             now = datetime.strptime(r.date_reference, '%Y-%m-%d')
        #             delta = relativedelta(now, dob)
        #             # self.age_reference = str(delta.years) + "y " + str(delta.months) + "m " + str(delta.days) + "d"
        #             r.age_reference = str(delta.years)
        #         else:
        #             r.age_reference = "No Date of Birth!"
        #     else:
        #         r.age_reference = "No Reference Date!"
        for r in self:
            if r.date_reference:
                dor = datetime.strptime(str(r.date_reference), '%Y-%m-%d')
                if r.birthday:
                    dob = datetime.strptime(str(r.birthday), '%Y-%m-%d')
                    if r.is_deceased and bool(r.date_death):
                        dod = datetime.strptime(str(r.date_death), '%Y-%m-%d')
                        delta = relativedelta(dod, dob)
                        is_deceased = _(' (deceased)')
                    elif r.is_deceased and not bool(r.date_death):
                        delta = relativedelta(dor, dob)
                        is_deceased = _(' (deceased?)')
                    else:
                        delta = relativedelta(dor, dob)
                        is_deceased = ''
                    years_months_days = '%d%s %d%s %d%s%s' % (
                        delta.years, _('y'), delta.months, _('m'), delta.days, _('d'),
                        is_deceased
                    )
                    years = '%d%s%s' % (
                        delta.years, _('y'),
                        is_deceased
                    )
                    r.age_reference = years_months_days
                    r.age_reference_years = years
                else:
                    r.age_reference = "No Date of Birth!"
                    r.age_reference_years = False
            else:
                r.age_reference = "No Date of Reference!"
                r.age_reference_years = False

    # @api.multi
    # def _compute_age_reference_suport(self):
    #     for r in self:
    #         if r.date_reference:
    #             if r.birthday:
    #                 dob = datetime.strptime(r.birthday, '%Y-%m-%d')
    #                 now = datetime.strptime(r.date_reference, '%Y-%m-%d')
    #                 delta = relativedelta(now, dob)
    #                 # self.age_reference = str(delta.years) + "y " + str(delta.months) + "m " + str(delta.days) + "d"
    #                 age_reference = str(delta.years)
    #             else:
    #                 age_reference = "No Date of Birth!"
    #         else:
    #             age_reference = "No Reference Date!"
    #         r.age_reference_suport = age_reference
    #         if r.age_reference != age_reference:
    #             record = self.env['clv.person'].search([('id', '=', r.id)])
    #             record.write({'date_reference': r.date_reference})

    force_is_deceased = fields.Boolean(
        string='Force Is Deceased',
        default=False
    )
    date_death = fields.Date(
        string='Deceased Date',
    )
    is_deceased = fields.Boolean(
        string='Is Deceased',
        compute='_compute_is_deceased',
        search='_search_is_deceased'
    )

    @api.multi
    def _compute_is_deceased(self):
        for record in self:
            if record.date_death:
                record.is_deceased = bool(record.date_death)
            record.is_deceased = bool(record.date_death) or record.force_is_deceased

    def _search_is_deceased(self, operator, value):
        if operator == 'like':
            operator = 'ilike'
        return ['|', ('date_death', '!=', False), ('force_is_deceased', '=', True)]

    # @api.multi
    # def _compute_age(self):
    #     """ Age computed depending based on the birth date in the
    #      membership request.
    #     """
    #     now = datetime.now()
    #     for record in self:
    #         if record.birthdate_date:
    #             birthdate_date = fields.Datetime.from_string(
    #                 record.birthdate_date,
    #             )
    #             if record.is_deceased:
    #                 date_death = fields.Datetime.from_string(record.date_death)
    #                 delta = relativedelta(date_death, birthdate_date)
    #                 is_deceased = _(' (deceased)')
    #             else:
    #                 delta = relativedelta(now, birthdate_date)
    #                 is_deceased = ''
    #             years_months_days = '%d%s %d%s %d%s%s' % (
    #                 delta.years, _('y'), delta.months, _('m'),
    #                 delta.days, _('d'), is_deceased
    #             )
    #             years = delta.years
    #         else:
    #             years_months_days = _('No DoB')
    #             years = False
    #         record.age = years_months_days
    #         if years:
    #             record.age_years = years

    is_absent = fields.Boolean(
        string='Is Absent'
    )

    gender = fields.Selection(
        [('M', 'Male'),
         ('F', 'Female'),
         ('O', 'Other'),
         ], string='Gender'
    )
    marital = fields.Selection(
        [('single', 'Single'),
         ('married', 'Married'),
         ('widower', 'Widower'),
         ('divorced', 'Divorced'),
         ('separated', 'Separated'),
         ('law marriage', 'law marriage'),
         ], string='Marital Status'
    )

    @api.model
    def _create_vals(self, vals):
        vals = super()._create_vals(vals)
        vals.update({
            'customer': True,
        })
        vals.update({
            'type': self._name,
        })
        return vals

    @api.model_cr_context
    def _get_default_image_path(self, vals):
        res = super()._get_default_image_path(vals)
        if res:
            return res
        image_path = get_module_resource(
            'clv_person', 'static/src/img', 'person-avatar.png',
        )
        return image_path

    spouse_id = fields.Many2one(comodel_name='clv.person', string='Spouse', ondelete='restrict')
    father_id = fields.Many2one(comodel_name='clv.person', string='Father', ondelete='restrict')
    mother_id = fields.Many2one(comodel_name='clv.person', string='Mother', ondelete='restrict')
    responsible_id = fields.Many2one(comodel_name='clv.person', string='Responsible', ondelete='restrict')
    caregiver_id = fields.Many2one(comodel_name='clv.person', string='Caregiver', ondelete='restrict')

    # identification_id = fields.Char(string='Person ID')
    # otherid = fields.Char(string='Other ID')

    @api.multi
    def write(self, values):
        ret = super().write(values)
        for record in self:
            if ('code' in values):
                if record.entity_code != values['code']:
                    vals = {}
                    vals['entity_code'] = values['code']
                    super().write(vals)
        return ret
