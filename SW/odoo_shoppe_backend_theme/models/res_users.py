# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ThemeResUser(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _get_company_theme(self):
        for res in self:
            if res.company_id.theme_type == 'company_theme':
                res.company_theme = True

    hide_theme_switcher = fields.Boolean("Theme Switcher", default=True)
    company_theme = fields.Boolean(compute="_get_company_theme")
    theme = fields.Selection([
        ('orange', 'Orange'),
        ('gray_black', 'Gray Black'),
        ('white', 'White Gray'),
        ('prussian', 'Dark Blue'),
        ('blue', 'Blue'),
        ('grey', 'Grey'),
        ('dark_red', 'Dark Red'),
        ('pink', 'Pink'),
        ('yellow_green', 'Yellow'),
    ], 'User Theme', default="orange")
    menu_style = fields.Selection([
        ('apps', 'Enterprise Menu'),
        ('sidemenu', 'Sidebar Menu')
    ], string="Menu Style", default="sidemenu")
    cover_bg = fields.Char(
        'Background Cover', default='/odoo_shoppe_backend_theme/static/src/img/cover/cover_black.jpg')
    allow_cover_bg = fields.Boolean("Allow Cover Background Cover", default=True)

    @api.model
    def create(self, vals):
        company = self.env['res.company'].search([('id', '=', vals.get('company_id'))])
        if company.theme_type == 'company_theme':
            vals.update({'theme': company.theme})
        else:
            vals.update({'theme': vals.get('theme')})
        return super(ThemeResUser, self).create(vals)

    @api.multi
    def write(self, data):
        res = super(ThemeResUser, self).write(data)
        if data.get('theme'):
            self.env['ir.qweb'].clear_caches()
        return res

    @api.multi
    def color_switcher_write(self, theme):
        self.sudo().write({'theme': theme})

    @api.multi
    def cover_switcher_write(self, cover):
        self.sudo().write({'cover_bg': cover})

    @api.multi
    def allow_cover_bg_write(self, res):
        self.sudo().write({'allow_cover_bg': res})
        vals = {'cover_bg': self.sudo().cover_bg}
        return vals

    @api.model
    def update_default_theme(self):
        users = self.env['res.users'].search([])
        for user in users.filtered(lambda l: not l.theme):
            if user.company_id.theme_type == 'user_theme':
                user.theme = 'orange'
            else:
                user.theme = user.company_id.theme
