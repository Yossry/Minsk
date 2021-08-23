odoo.define('uppercrust_backend_theme.CrashManager', function (require) {
    "use strict";

    var CrashManager = require('web.CrashManager');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    var _lt = core._lt;

    var map_title = {
        user_error: _lt('Warning'),
        warning: _lt('Warning'),
        access_error: _lt('Access Error'),
        missing_error: _lt('Missing Record'),
        validation_error: _lt('Validation Error'),
        except_orm: _lt('Global Business Error'),
        access_denied: _lt('Access Denied'),
    };

    CrashManager.include({
        rpc_error: function (error) {
            var self = this;
            if (!this.active) {
                return;
            }
            if (this.connection_lost) {
                return;
            }
            if (error.code === -32098) {
                this.connection_lost = true;
                this.$indicator = $('<div class="oe_cu_indicator_warning">' + _t("Trying to reconnect... ") + '<i class="fa fa-refresh fa-spin"></i></div>').fadeIn("slow");
                this.$indicator.prependTo("body");
                var timeinterval = setInterval(function () {
                    ajax.jsonRpc('/web/webclient/version_info').then(function () {
                        clearInterval(timeinterval);
                        self.$indicator.animate({backgroundColor: '#00aa00', opacity: 1}, 1000);
                        self.$indicator.html(_t("You are back online"));
                        $('<div class="oe_cu_indicator_sucsess">' + _t("Trying to reconnect... "));
                        self.$indicator.delay(2000).slideUp('slow', function () {
                            $(this).remove();
                            self.$indicator.remove();
                        });
                        self.connection_lost = false;
                    });
                }, 2000);
                return;
            }
            var handler = core.crash_registry.get(error.data.name, true);
            if (handler) {
                new (handler)(this, error).display();
                return;
            }
            if (error.data.name === "odoo.http.SessionExpiredException" || error.data.name === "werkzeug.exceptions.Forbidden") {
                this.show_warning({
                    type: _t("Odoo Session Expired"),
                    data: {message: _t("Your Odoo session expired. Please refresh the current web page.")}
                });
                return;
            }
            if (_.has(map_title, error.data.exception_type)) {
                if (error.data.exception_type === 'except_orm') {
                    if (error.data.arguments[1]) {
                        error = _.extend({}, error,
                                {
                                    data: _.extend({}, error.data,
                                            {
                                                message: error.data.arguments[1],
                                                title: error.data.arguments[0] !== 'Warning' ? (" - " + error.data.arguments[0]) : '',
                                            })
                                });
                    }
                    else {
                        error = _.extend({}, error,
                                {
                                    data: _.extend({}, error.data,
                                            {
                                                message: error.data.arguments[0],
                                                title: '',
                                            })
                                });
                    }
                }
                else {
                    error = _.extend({}, error,
                            {
                                data: _.extend({}, error.data,
                                        {
                                            message: error.data.arguments[0],
                                            title: map_title[error.data.exception_type] !== 'Warning' ? (" - " + map_title[error.data.exception_type]) : '',
                                        })
                            });
                }

                this.show_warning(error);
                //InternalError

            } else {
                this.show_error(error);
            }
        },
    });
});
