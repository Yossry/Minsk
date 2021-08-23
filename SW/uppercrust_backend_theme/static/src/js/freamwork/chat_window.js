odoo.define('uppercrust_backend_theme.ThreadWindow', function (require) {
    "use strict";

    var ThreadWindow = require('mail.ThreadWindow');

    ThreadWindow.include({
        start: function () {
            this._super.apply(this, arguments);
            this.$body = $('body');
            this.$body.addClass('ad-chat-window');
        },
        close: function () {
            event.stopPropagation();
            event.preventDefault();
            if ((this.$body.find('.o_thread_window').length - 1) === 0) {
                this.$body.removeClass('ad-chat-window');
            }
            if (this.hasThread()) {
                this._thread.close();
            } else {
                this.trigger_up('close_blank_thread_window');
            }
        },
    });

});