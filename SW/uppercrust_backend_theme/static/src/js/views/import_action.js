odoo.define('uppercrust_backend_theme.Import', function (require) {
    "use strict";
    var base_import = require('base_import.import');

    base_import.DataImport.include({
        events: _.extend({}, base_import.DataImport.prototype.events, {
            'click a.oe_import_toggle': function (e) {
                e.preventDefault();
                this.$('.oe_import_options').toggle();
                this.$('.oe_import_toggle').toggleClass('open');
            },
        })
    });
});