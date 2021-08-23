odoo.define('uppercrust_backend_theme.AppsMenu', function (require) {
    "use strict";

    var AppsMenu = require('web.AppsMenu');
    var session = require('web.session');

    AppsMenu.include({
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._activeApp = undefined;
            this.company_id = session.company_id;
            this._apps = _.map(menuData.children, function (appMenuData) {
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    menuIcon : '/web/image/ir.ui.menu/' + appMenuData.id + '/web_icon_data/60x60'
                };
            });
        },
    });
});