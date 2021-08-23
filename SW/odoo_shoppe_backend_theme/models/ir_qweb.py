# # -*- coding: utf-8 -*-

from openerp import models, tools
from odoo.addons.base.models.qweb import QWeb


class IrQWeb(models.AbstractModel, QWeb):
    _inherit = 'ir.qweb'

    @tools.conditional(
        # in non-xml-debug mode we want assets to be cached forever, and the admin can force a cache clear
        # by restarting the server after updating the source code (or using the "Clear server cache" in debug tools)
        'xml' not in tools.config['dev_mode'],
        tools.ormcache_context(
            'xmlid', 'options.get("lang", "en_US")', 'css', 'js', 'debug', 'kw.get("async")',
            'async_load', keys=("website_id",)),
    )
    def _get_asset_nodes(self, xmlid, options, css=True, js=True, debug=False,
                         async_load=False, values=None, **kw):
        if 'async' in kw:
            async_load = kw['async']
        files, remains = self._get_asset_content(xmlid, options)
        asset = self.get_asset_bundle(xmlid, files, env=self.env)
        if xmlid == 'odoo_shoppe_backend_theme.osbt_theme_assets':
            debug = 'assets'
        remains = [node for node in remains if (css and node[0] == 'link') or (js and node[0] != 'link')]
        return remains + asset.to_node(css=css, js=js, debug=debug, async_load=async_load)
