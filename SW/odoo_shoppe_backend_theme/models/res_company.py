# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    about_company = fields.Html(string='About')
    theme_type = fields.Selection([
        ('company_theme', 'Based on Company Theme'),
        ('user_theme', 'Based on User Theme')], default="user_theme", string="Theme Type")
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
    ], 'Company Theme', default="orange")
    app_background_image = fields.Binary("App Background Image")
    theme_lables_color = fields.Char("Theme Label Color")

    @api.multi
    def about_company_data(self):
        user = self.env['res.users'].search([('id', '=', self._uid)])
        company_about = user.company_id.about_company
        return company_about

    @api.multi
    def write(self, data):
        users = self.env['res.users'].search([('company_id', '=', self.id)])
        if data.get('theme_type') == 'user_theme':
            for user in users:
                user.theme = 'orange'
                user.hide_theme_switcher = True
        else:
            for user in users:
                if data.get('theme'):
                    theme = data['theme']
                else:
                    theme = self.theme
                user.theme = theme
                user.hide_theme_switcher = False
        self.env['ir.qweb'].clear_caches()
        return super(ResCompany, self).write(data)
