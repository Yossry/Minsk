# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import threading
import base64
from datetime import datetime

from openerp import api, fields, models, tools


class AbstractPartnerEntity(models.AbstractModel):
    _name = 'clv.abstract.partner_entity'
    _description = 'Abstract Partner Entity'
    _inherits = {'res.partner': 'partner_id'}
    # _inherit = ['mail.thread']

    _order = 'name'

    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )

    # type = fields.Selection(
    #     default=lambda s: s._name,
    #     related='partner_id.type',
    # )

    code = fields.Char(string='Partner Entity Code', required=False)

    date_inclusion = fields.Datetime(
        string="Inclusion Date", required=False, readonly=False,
        default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    contact_info_is_unavailable = fields.Boolean(
        string='Contact Information is unavailable',
        default=False,
    )

    # Redefine `active` so that it is managed independently from partner.
    active = fields.Boolean(
        default=True,
    )

    related_partner_id = fields.Integer(
        string='Related Partner ID',
        compute='_compute_related_partner_id'
    )

    @api.depends('partner_id')
    def _compute_related_partner_id(self):
        for register in self:
            if register.partner_id.id is not False:
                register.related_partner_id = register.partner_id.id
            else:
                register.related_partner_id = False

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals = self._create_vals(vals)
        return super().create(vals)

    @api.multi
    def toggle_active(self):
        """ It toggles entity and partner activation. """
        for record in self:
            super().toggle_active()
            if record.active:
                record.partner_id.active = True
            else:
                entities = record.env[record._name].search([
                    ('partner_id', 'child_of', record.partner_id.id),
                    ('parent_id', 'child_of', record.partner_id.id),
                    ('active', '=', True),
                ])
                if not entities:
                    record.partner_id.active = False

    @api.model
    def _create_vals(self, vals):
        """ Override this in child classes in order to add default values. """
        if self._allow_image_create(vals):
            vals['image'] = self._get_default_image_encoded(vals)
        return vals

    @api.model_cr_context
    def _allow_image_create(self, vals):
        """ It determines if conditions are present that should stop image gen.

        This is implemented so that tests aren't wildly creating images left
         and right for no reason. Child classes could also inherit this to
         provide custom rules for image generation.

        Note that this method explicitly allows image generation if
         ``__image_create_allow`` is a ``True`` value in the context. Any
         child that chooses to provide custom rules shall also adhere to this
         context, unless there is a documented reason to not do so.
        """
        if vals.get('image'):
            return False
        if any((getattr(threading.currentThread(), 'testing', False),
                self._context.get('install_mode'))):
            if not self.env.context.get('__image_create_allow'):
                return False
        return True

    @api.model_cr_context
    def _create_default_image(self, vals):
        base64_image = self._get_default_image_encoded(vals)
        if not base64_image:
            return
        return tools.image_resize_image_big(base64_image)

    def _get_default_image_encoded(self, vals):
        """ It returns the base64 encoded image string for the default avatar.

        Args:
            vals (dict): Values dict as passed to create.

        Returns:
            str: A base64 encoded image.
            NoneType: None if no result.
        """
        colorize, image_path, image = False, False, False

        image_path = self._get_default_image_path(vals)
        if not image_path:
            return

        if image_path:
            with open(image_path, 'rb') as f:
                image = f.read()

        if image and colorize:
            image = tools.image_colorize(image)

        return base64.b64encode(image)

    @api.model_cr_context
    def _get_default_image_path(self, vals):
        """ Overload this in child classes in order to add a default image.

        Example:

            .. code-block:: python

            @api.model
            def _get_default_image_path(self, vals):
                res = super()._get_default_image_path(vals)
                if res:
                    return res
                image_path = odoo.modules.get_module_resource(
                    'base', 'static/src/img', 'patient-avatar.png',
                )
                return image_path

        Args:
            vals (dict): Values dict as passed to create.

        Returns:
            str: A file path to the image on disk.
            bool: False if error.
            NoneType: None if no result.
        """
        return  # pragma: no cover

    def toggle(self, attr):
        if getattr(self, attr) is True:
            self.write({attr: False})
        elif getattr(self, attr) is False:
            self.write({attr: True})

    # @api.multi
    # def do_set_contact_info_as_unavailable(self):

    #     for record in self:

    #         data_values = {}

    #         data_values['contact_info_is_unavailable'] = True

    #         data_values['street'] = False
    #         data_values['street2'] = False
    #         data_values['zip'] = False
    #         data_values['city'] = False
    #         data_values['state_id'] = False
    #         data_values['country_id'] = False
    #         # data_values['phone'] = False
    #         # data_values['mobile'] = False

    #         record.write(data_values)

    #     return True
