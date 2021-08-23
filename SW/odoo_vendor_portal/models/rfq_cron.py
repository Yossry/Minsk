# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _


class VendorRfqCron(models.TransientModel):
    _name = "vendor.rfq.cron"

    @api.model
    def _done_rfq_cron(self):
        dateFormat = '%Y-%m-%d'
        crntDate = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        crntDate = crntDate.split(' ')[0]
        crntDate = datetime.strptime(crntDate, dateFormat)
        progressRfqs = self.env['vendor.rfq'].search([('state', '=', 'sent')])
        IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo()
        basedOn = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.done_rfq_basedon')
        for rfqObj in progressRfqs:
            if rfqObj.close_date:
                diffdate = rfqObj.close_date - crntDate.date()
                dayLeft = diffdate.days
                if dayLeft < 0:
                    self.mark_done_cron(rfqObj, basedOn)
        return True

    @api.model
    def mark_done_cron(self, rfqObj, basedOn):
        qootedObjsSorted = []
        if basedOn == 2:
            qootedObjsSorted = sorted(rfqObj.vendor_rfq_history, key=lambda qootedObj : qootedObj.quoted_del_date)
        else:
            qootedObjsSorted = sorted(rfqObj.vendor_rfq_history, key=lambda qootedObj : qootedObj.quoted_price)
        if qootedObjsSorted:
            try:
                rfqObj.assign_vendor = qootedObjsSorted[0].name.id
                rfqObj.assign_vendor_price = qootedObjsSorted[0].quoted_price
                if qootedObjsSorted[0].quoted_del_date:
                    rfqObj.vendor_del_date = qootedObjsSorted[0].quoted_del_date
                rfqObj.state = 'done'
                self.env['vendor.rfq'].send_mail_done(
                    rfqObj, qootedObjsSorted[0].quoted_price, qootedObjsSorted[0].quoted_del_date, qootedObjsSorted[0].name)
            except Exception as e:
                pass

        return True
