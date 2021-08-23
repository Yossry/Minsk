# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api, fields


class GlobalSearchConfigTemplate(models.Model):
    _name = 'global.search.config.template'
    _description = 'Global Search Configuration Template'
    _rec_name = 'model_id'

    @api.multi
    def _search_model(self):
        """
            Returns model list which are accessible for login user
        """
        models = self.env['ir.model'].search([('state', '!=', 'manual'), ('transient', '=', False)])
        access_model = self.env['ir.model.access']
        model_ids = [model.id for model in models if
                     access_model.sudo(user=self.env.user.id).check(model.model, 'read', raise_exception=False)]
        return [('id', 'in', model_ids)]

    model_id = fields.Many2one('ir.model', 'Model', domain=_search_model, required=True)
    field_ids = fields.Many2many('ir.model.fields', string='Fields',
                                 domain="[('model_id', '=', model_id), ('name', '!=', 'id'), ('ttype', '!=', 'boolean'), ('selectable', '=', True)]",
                                 required="1")

    _sql_constraints = [
        ('uniq_model',
         "UNIQUE(model_id)",
         "The Model must be unique."),
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_ids = [(6, 0, [])]

    @api.multi
    def apply_changes_in_searches(self):
        """ Its calling for effects on searches."""
        searches = self.env['global.search.config'].search([('batch_id', '=', False), ('template_id', 'in', self.ids)])
        for rec in searches:
            if not rec.customized:
                rec.set_values_template_batch(rec.template_id)
        return True


class GlobalSearchConfig(models.Model):
    _name = 'global.search.config'
    _description = 'Global Search Configuration'
    _rec_name = 'model_id'

    template_id = fields.Many2one('global.search.config.template', 'Template', domian="[('id', in, [])]")
    batch_id = fields.Many2one('global.search.config.batch', string="Batch")
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, copy=False)
    customized = fields.Boolean('Customized')
    model_id = fields.Many2one('ir.model', 'Model', required=True, )
    field_ids = fields.Many2many('ir.model.fields', string='Fields',
                                 domain="[('model_id', '=', model_id), ('name', '!=', 'id'), "
                                        "('ttype', '!=', 'boolean'), ('selectable', '=', True)]",
                                 required="1", order="ir_model_fields_id.field_description desc")

    _sql_constraints = [
        ('uniq_template_user',
         "UNIQUE(template_id, user_id)",
         "The template must be unique per user."),
    ]

    @api.multi
    def write(self, vals):
        '''Override to manage customized boolean'''
        if 'customized' not in vals and ((vals.get('user_id') and len(vals.keys()) > 1) or not vals.get('user_id')):
            vals['customized'] = True
        if 'template_id' in vals and not vals.get('model_id', False):
            vals['model_id'] = self.env['global.search.config.template'].search(
                [('id', '=', vals.get('template_id'))]).model_id.id
        return super(GlobalSearchConfig, self).write(vals)

    @api.model
    def create(self, vals):
        '''Override check the values'''
        if 'template_id' in vals and not vals.get('model_id', False):
            vals['model_id'] = self.env['global.search.config.template'].search(
                [('id', '=', vals.get('template_id'))]).model_id.id
        return super(GlobalSearchConfig, self).create(vals)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        '''Returns domain to filter template whose model are accessible for selected user.'''
        dom = {'template_id': [('id', 'in', [])]}
        if self.user_id:
            models = self.env['ir.model'].search([('state', '!=', 'manual'), ('transient', '=', False)])
            access_model = self.env['ir.model.access']
            model_ids = [model.id for model in models if
                         access_model.sudo(user=self.user_id.id).check(model.model, 'read', raise_exception=False)]
            dom['template_id'] = [('model_id', 'in', model_ids)]
            dom['model_id'] = [('id', 'in', model_ids)]
        return {'domain': dom}

    @api.onchange('template_id')
    def _onchange_template_id(self):
        '''To set fields as per template selection.'''
        for rec in self:
            rec.set_values_template_batch(rec.template_id)

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.template_id:
            self._onchange_template_id()
        else:
            self.field_ids = [(6, 0, [])]

    @api.multi
    def set_values_template_batch(self, template_batch_id):
        for rec in self:
            rec.field_ids = [(6, 0, template_batch_id.field_ids.ids)]
            rec.model_id = template_batch_id.model_id.id
            rec.customized = False

    @api.multi
    def set_default_template_batch(self):
        '''Set default button.
        To set fields as per template or batch selection. '''
        for rec in self:
            rec.set_values_template_batch(rec.batch_id or rec.template_id)
