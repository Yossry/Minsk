odoo.define('uppercrust_backend_theme.Attachments', function (require) {
    "use strict";

    var core = require('web.core');
    var Sidebar = require('web.Sidebar');

    var QWeb = core.qweb;
    var _t = core._t;

    var mapping = [
        ['file-image-o', /^image\//],
        ['file-audio-o', /^audio\//],
        ['file-video-o', /^video\//],
        ['file-pdf-o', 'application/pdf'],
        ['file-text-o', 'text/plain'],
        ['file-code-o', [
            'text/html',
            'text/javascript',
            'application/javascript'
        ]],
        ['file-archive-o', [
            /^application\/x-(g?tar|xz|compress|bzip2|g?zip)$/,
            /^application\/x-(7z|rar|zip)-compressed$/,
            /^application\/(zip|gzip|tar)$/,
            'application/rar'
        ]],
        ['file-word-o', [
            /ms-?word/, 'application/vnd.oasis.opendocument.text',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]],
        ['file-powerpoint-o', [
            /ms-?powerpoint/,
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ]],
        ['file-excel-o', [
            /ms-?excel/,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]],
        ['file-o']
    ];
    Sidebar.include({
        _redraw: function () {
            this._super.apply(this, arguments);
            var self = this, flag = true;
            // Hides Sidebar sections when item list is empty
            _.each(this.$('.o_dropdown'), function (el) {
                var $dropdown = $(el);
                if (!$dropdown.find('.dropdown-item').length) {
                    $dropdown.hide();
                } else if (flag) {
                    $dropdown.addClass('ad_active show');
                    flag = false;
                }
            });
            this.$('button.o_dropdown_toggler_btn').on('click', function (e) {
                self.$('.list-element').removeClass('ad_active');
                $(e.target).parent().addClass('ad_active');
            });
        },
        match: function (mimetype, cond) {
            var self = this;
            if (Array.isArray(cond)) {
                return cond.reduce(function (v, c) {
                    return v || self.match(mimetype, c)
                }, false)
            } else if (cond instanceof RegExp) {
                return cond.test(mimetype)
            } else if (cond === undefined) {
                return true
            } else {
                return mimetype === cond
            }
        },
        _processAttachments: function (attachments) {
            //to display number in name if more then one attachment which has same name.
            var self = this;
            _.chain(attachments)
                    .groupBy(function (attachment) {
                        return attachment.name;
                    })
                    .each(function (attachment) {
                        if (attachment.length > 1) {
                            _.map(attachment, function (attachment, i) {
                                attachment.name = _.str.sprintf(_t("%s (%s)"), attachment.name, i + 1);
                            });
                        }
                    });
            _.each(attachments, function (a) {
                a.label = a.name;
                for (var i = 0; i < mapping.length; i++) {
                    if (self.match(a.mimetype, mapping[i][1])) {
                        a['icon'] = mapping[i][0];
                        return mapping[i][0];
                    }
                }
                if (a.type === "binary") {
                    a.url = '/web/content/' + a.id + '?download=true';
                }
                a.create_date = field_utils.parse.datetime(a.create_date, 'create_date', {isUTC: true});
                a.create_date_string = field_utils.format.datetime(a.create_date, 'create_date', self.env.context.params);
                a.write_date = field_utils.parse.datetime(a.write_date, 'write_date', {isUTC: true});
                a.write_date_string = field_utils.format.datetime(a.write_date, 'write_date', self.env.context.params);
            });
            this.items.files = attachments;
        },
        _updateAttachments: function () {
            var activeId = this.env.activeIds[0];
            if (!activeId) {
                this.items.files = [];
                return $.when();
            } else {
                var domain = [
                    ['res_model', '=', this.env.model],
                    ['res_id', '=', activeId],
                    ['type', 'in', ['binary', 'url']]
                ];
                var fields = ['name', 'url', 'type', 'mimetype',
                    'create_uid', 'create_date', 'write_uid', 'write_date'];
                return this._rpc({
                    model: 'ir.attachment',
                    method: 'search_read',
                    context: this.env.context,
                    domain: domain,
                    fields: fields,
                }).then(this._processAttachments.bind(this));
            }
        },
    });
});
