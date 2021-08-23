# -*- coding: utf-8 -*-
# Part of Synconics. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import os

from odoo import _, api, fields, models
from odoo.exceptions import UserError


static_dict_theme = {
    '$brand-primary': '#072635;',
    '$brand-secondary': '#1983a4;',
    '$button-box': '#0b3a49;',
    '$heading': '#1983a4;',
    '$Label': '#0b3a49;',
    '$Label-value': '#0b3a49;',
    '$link': '#1983a4;',
    '$notbook': '#0b3a49;',
    '$tooltip': '#072630;',
    '$border': '#e6e9ea;',
    '$menu-main-title': '#0b3a49;'
}

tag_dict_theme = {
    '$brand-tag-info': '#00b3e5;',
    '$brand-tag-danger': '#ca0c05;',
    '$brand-tag-success': '#00aa00;',
    '$brand-tag-warning': '#e47e01;',
    '$brand-tag-primary': '#005ba9;',
    '$brand-tag-muted': '#717171;'
}


class IrWebTheme(models.Model):
    _name = "ir.web.theme"
    _description = 'Customize Web Theme'

    leftbar_color = fields.Char(string='Custom Color', required=True, default="#875a7b")
    menu_color = fields.Char(string='Menu', required=True, default="#666666")
    border_color = fields.Char(string='Border', required=True, default="#cccccc")
    buttons_color = fields.Char(string='Buttons Color', required=True, default="#00a09d")
    button_box = fields.Char(string='Button Box', required=True, default="#666666")
    heading_color = fields.Char(string='Heading Color', required=True, default="#2f3136")
    label_color = fields.Char(string='Label', required=True, default="#666666")
    label_value_color = fields.Char(string='Label Value Color', required=True, default="#666666")
    link_color = fields.Char(string='Link Color', required=True, default="#00a09d")
    panel_title_color = fields.Char(string='Panel Title Color', required=True, default="#2f3136")
    tooltip_color = fields.Char(string='Tooltip Color', required=True, default="#875a7b")
    tag_info = fields.Char(string="Tag Info", default="#00b3e5")
    tag_danger = fields.Char(string="Tag Danger", default="#ca0c05")
    tag_success = fields.Char(string="Tag Success", default="#00aa00")
    tag_warning = fields.Char(string="Tag Warning", default="#e47e01")
    tag_primary = fields.Char(string="Tag Primary", default="#005ba9")
    tag_muted = fields.Char(string="Tag Muted", default="#717171")

    def replace_file(self, file_path, static_dict):
        try:
            with open(file_path, 'w+') as new_file:
                for key, value in static_dict.items():
                    line = ''.join([key, ': ', value, ';\n'])
                    new_file.write(line)
            new_file.close()
        except Exception as e:
            raise UserError(_("Please follow the readme file. Contact to Administrator."
                              "\n %s") % e)

    @api.multi
    def set_customize_theme(self, theme_id, form_values):
        self.env['ir.config_parameter'].sudo().set_param("uppercrust_backend_theme.selected_theme", theme_id)
        is_backend_module_install = self.env['ir.config_parameter'].sudo().get_param("is_login_install")
        is_tag_module_install = self.env['ir.config_parameter'].sudo().get_param("is_tag_install")
        try:
            path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            theme_path = path + "/uppercrust_backend_theme/static/src/scss/variables.scss"
            backend_login = path + "/backend_login/static/src/scss/variable.scss"
            status_tag = path + "/web_status_tags/static/src/scss/variable.scss"
        except Exception as e:
            raise UserError(_("Please Contact to Administrator. \n %s") % e)

        # Backend Theme Changes
        if form_values.get('leftbar_color', False):
            static_dict_theme.update({'$brand-primary': form_values['leftbar_color']})

        if form_values.get('buttons_color', False):
            static_dict_theme.update({'$brand-secondary': form_values['buttons_color']})

        if form_values.get('button_box', False):
            static_dict_theme.update({'$button-box': form_values['button_box']})

        if form_values.get('heading_color', False):
            static_dict_theme.update({'$heading': form_values['heading_color']})

        if form_values.get('label_color', False):
            static_dict_theme.update({'$Label': form_values['label_color']})

        if form_values.get('label_value_color', False):
            static_dict_theme.update({'$Label-value': form_values['label_value_color']})

        if form_values.get('link_color', False):
            static_dict_theme.update({'$link': form_values['link_color']})

        if form_values.get('panel_title_color', False):
            static_dict_theme.update({'$notbook': form_values['panel_title_color']})

        if form_values.get('tooltip_color', False):
            static_dict_theme.update({'$tooltip': form_values['tooltip_color']})

        if form_values.get('menu_color', False):
            static_dict_theme.update({'$menu-main-title': form_values['menu_color']})

        if form_values.get('border_color', False):
            static_dict_theme.update({'$border': form_values['border_color']})

        self.replace_file(theme_path, static_dict_theme)

        # Backend Login Changes
        if is_backend_module_install and form_values.get('leftbar_color', False):
            self.replace_file(backend_login, {'$brand-primary': form_values.get['leftbar_color']})

        # Web Status Tag Changes
        if is_tag_module_install:
            if form_values.get('tag_info', False):
                tag_dict_theme.update({'$brand-tag-info': form_values['tag_info']})

            if form_values.get('tag_danger', False):
                tag_dict_theme.update({'$brand-tag-danger': form_values['tag_danger']})

            if form_values.get('tag_success', False):
                tag_dict_theme.update({'$brand-tag-success': form_values['tag_success']})

            if form_values.get('tag_warning', False):
                tag_dict_theme.update({'$brand-tag-warning': form_values['tag_warning']})

            if form_values.get('tag_primary', False):
                tag_dict_theme.update({'$brand-tag-primary': form_values['tag_primary']})

            if form_values.get('tag_muted', False):
                tag_dict_theme.update({'$brand-tag-muted': form_values['tag_muted']})

            self.replace_file(status_tag, tag_dict_theme)
