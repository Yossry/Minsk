# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db, redirect_with_hash
from odoo.http import request


class KsHome(Home, http.Controller):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if kw.get('debug') == "assets":
            if request.env['ir.config_parameter'].sudo().get_param('ks_hide_debug_assets_permission'):
                if not request.env.user.browse(request.session.uid)._is_admin():
                    return redirect_with_hash('/web')

        return super(KsHome, self).web_client(s_action=s_action, **kw)


