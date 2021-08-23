odoo.define('email_cc_bcc.model.Message', function (require) {
    "use strict";

    var MailMessage = require('mail.model.Message');

    var CcBccMessage = MailMessage.include({
        init: function (parent, data) {
            this._super.apply(this, arguments);
            this.cc_partners = data.cc_partners;
            this.email_cc = data.email_cc;
            this.bcc_partners = data.bcc_partners;
            this.email_bcc = data.email_bcc;
        },

    });

    return CcBccMessage;
});
