# coding: utf-8
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import string
from random import choice

from odoo import api, fields, models
from odoo.addons.base.res.res_users import\
    name_boolean_group, name_selection_groups


class ResCompanyCreateWizard(models.TransientModel):
    _name = 'res.company.create.wizard'

    _PASSWORD_SIZE = 8

    company_name = fields.Char(string='Name', required=True)

    company_code = fields.Char(string='Code')

    parent_company_id = fields.Many2one(
        comodel_name='res.company', string='Parent Company')

    company_vat = fields.Char(string='Tax ID')

    company_registry = fields.Char(string='Company Registry')

    # Partner and company fields
    company_street = fields.Char(string='Street')

    company_street2 = fields.Char(string='Street complement')

    company_city = fields.Char(string='City')

    company_zip = fields.Char(string='ZIP')

    company_state_id = fields.Many2one(
        comodel_name='res.country.state', string='State')

    company_country_id = fields.Many2one(
        comodel_name='res.country', string='Country')

    company_website = fields.Char(string='Website')

    company_email = fields.Char(string='Email')

    company_phone = fields.Char(string='Phone')

    # User Fields
    create_user = fields.Boolean(string='Create User')

    user_name = fields.Char(string='Name')

    user_login = fields.Char(
        string='Login', help="Let empty to use the email as login")

    user_email = fields.Char(string='Email')

    user_password = fields.Char(
        string='Password', default=lambda s: s._default_user_password())

    user_group_ids = fields.Many2many(
        string='Groups', comodel_name='res.groups',
        default=lambda s: s._default_user_group_ids())

    # Technical hidden fields
    company_id = fields.Many2one(comodel_name='res.company')

    user_id = fields.Many2one(comodel_name='res.users')

    # Default Section
    def _default_user_password(self):
        characters = string.ascii_letters + string.digits
        return "".join(choice(characters) for x in range(self._PASSWORD_SIZE))

    def _default_user_group_ids(self):
        return self._prepare_user_group_ids_from_default_get()

    # Button Section
    @api.multi
    def button_create_company(self):
        self.ensure_one()
        self._create_company()
        return True

    # Overloadable Prepare Function
    @api.multi
    def _prepare_company(self):
        self.ensure_one()
        return {
            'name': self.company_name,
            'code': self.company_code,
            'parent_id': self.parent_company_id.id,
            'street': self.company_street,
            'street2': self.company_street2,
            'city': self.company_city,
            'state_id': self.company_state_id,
            'country_id': self.company_country_id,
            'website': self.company_website,
            'email': self.company_email,
            'phone': self.company_phone,
            'vat': self.company_vat,
            'company_registry': self.company_registry,
        }

    @api.multi
    def _prepare_partner(self):
        self.ensure_one()
        return {
            'customer': False,
            'supplier': False,
            'active': False,
        }

    @api.multi
    def _prepare_user(self):
        self.ensure_one()
        return {
            'customer': False,
            'name': self.user_name,
            'login': self.user_login or self.user_email,
            'email': self.user_email,
            'new_password': self.user_password,
            'company_id': self.company_id.id,
            'company_ids': [(4, self.company_id.id)],
            'groups_id': [(4, x.id) for x in self.user_group_ids],
        }

    @api.model
    def _prepare_user_group_ids_from_default_get(self):
        group_obj = self.env['res.groups']
        user_obj = self.env['res.users']
        res1 = group_obj.get_groups_by_application()
        fields = []
        for item in res1:
            if item[1] == 'boolean':
                for group in item[2]:
                    fields.append(name_boolean_group(group.id))
            elif item[1] == 'selection':
                fields.append(name_selection_groups(item[2].ids))
        res2 = user_obj.default_get(fields)
        return res2['groups_id'][0][2]

    @api.multi
    def _create_company(self):
        self.ensure_one()
        company_obj = self.env['res.company']
        user_obj = self.env['res.users']
        # Create Company
        self.company_id = company_obj.sudo().create(self._prepare_company())

        # Swith current user to the new company
        self.env.user.write({
            'company_id': self.company_id.id,
            'company_ids': [(4, self.company_id.id)],
        })
        # Clear cache, specially to reset obsoleted cached domain
        # ./odoo/tools/cache.py (_compute_domain)
        self.env.clear()

        # Manage Extra Data in associated partner
        self.company_id.partner_id.write(self._prepare_partner())

        # Create User if required
        if self.create_user:
            self.user_id = user_obj.create(self._prepare_user())
