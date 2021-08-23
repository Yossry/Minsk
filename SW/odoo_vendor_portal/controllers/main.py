# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from collections import OrderedDict

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortal(CustomerPortal):


    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        vendorRfq = request.env['vendor.rfq'].sudo()
        rfqCount = vendorRfq.search_count(['|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('vendor_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel', 'done'])
        ])

        values.update({
            'rfq_count': rfqCount,
        })
        return values

    def _rfq_check_access(self, rfq_id, access_token=None):
        rfqObj = request.env['vendor.rfq'].browse([rfq_id])
        rfqObjSudo = rfqObj.sudo()
        try:
            rfqObj.check_access_rights('read')
            rfqObj.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(rfqObjSudo.access_token, access_token):
                raise
        return rfqObjSudo

    def _rfq_get_page_view_values(self, rfqObjSudo, access_token, **kwargs):
        rfqHistoryModel = request.env['vendor.rfqhistory'].sudo()
        currentLogUser = request.env.user
        loggedPartner = currentLogUser.partner_id
        vendorIds = rfqObjSudo.vendor_ids
        offerPrice = 'yes'
        if loggedPartner not in vendorIds:
            offerPrice = 'no'
        rfqHstry = rfqHistoryModel.search([('vendorrfq_id', '=', rfqObjSudo.id), ('name', '=', loggedPartner.id)])
        mpPrice, myEstDel, myNote = rfqHstry.quoted_price, rfqHstry.quoted_del_date, rfqHstry.quoted_note if rfqHstry else ''
        IrConfigPrmtrSudo = request.env['ir.config_parameter'].sudo()
        sumbitMsg = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.msg_quote_submit') or "Thanks! We have received your quote. We will revert back to you if your quote will get approved."
        acceptMsg = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.msg_quote_accecpt') or "Congratulations! we have accepted your quotation, we'll soon create the purchase order for you. We will look forward to a long-term business relationship with you"
        cancelMsg = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.msg_rfq_cancel') or "Sorry! This RFQ has been cancelled."
        poMsg = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.msg_po_create') or "Congratulations! A Purchase Order has been created for this RFQ."
        rejectMsg = ''
        if rfqObjSudo.assign_vendor and rfqObjSudo.assign_vendor.id != loggedPartner.id:
            rejectMsg = IrConfigPrmtrSudo.get_param('odoo_vendor_portal.msg_rfq_reject') or "We regret that your quote has not been accepted. We will be glad to give you an another opportunity soon."
        values = {
            'rfq_obj': rfqObjSudo,
            'my_price' : mpPrice,
            'offer_price' : offerPrice,
            'my_del_date' : myEstDel,
            'my_note' : myNote,
            'msg_submit' : sumbitMsg,
            'msg_accept' : acceptMsg,
            'msg_cancel' : cancelMsg,
            'msg_reject' : rejectMsg,
            'msg_po' : poMsg,
            'page_name': 'rfq',
            'bootstrap_formatting': True,
            'report_type': 'html',
        }
        if access_token:
            values['access_token'] = access_token

        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        history = request.session.get('my_rfqs_history', [])
        values.update(get_records_pager(history, rfqObjSudo))

        return values


    @http.route(['/my/rfqrequests', '/my/rfqrequests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_rfqrequest(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        vendorRfq = request.env['vendor.rfq'].sudo()
        rfqHistoryModel = request.env['vendor.rfqhistory'].sudo()

        domain = ['|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('vendor_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel', 'done'])
        ]

        searchbar_sortings = {
            'createdate': {'label': _('Created Date'), 'order': 'create_date desc'},
            'date': {'label': _('Closing Date'), 'order': 'close_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('State'), 'order': 'state desc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'createdate'
        sort_order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['sent', 'done', 'cancel'])]},
            'progress': {'label': _('In Progress'), 'domain': [('state', '=', 'sent')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        rfqCount = vendorRfq.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/rfqrequests",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=rfqCount,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        pageRfqrequest = vendorRfq.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_rfqs_history'] = pageRfqrequest.ids[:100]
        quoted = {}
        for rfqObj in pageRfqrequest:
            rfqId = rfqObj.id
            rfqHstry = rfqHistoryModel.search([('vendorrfq_id', '=', rfqId), ('name', '=', partner.id)])
            quoted.update({rfqId : 'no'})
            if rfqHstry:
                quoted.update({rfqId : 'yes'})

        values.update({
            'date': date_begin,
            'page_rfqrequest': pageRfqrequest.sudo(),
            'page_name': 'rfq',
            'quote' : quoted,
            'pager': pager,
            'default_url': '/my/rfqrequests',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("odoo_vendor_portal.portal_my_page_rfq", values)

    @http.route(['/my/rfqrequests/<int:order>'], type='http', auth="user", website=True)
    def rfq_followup(self, order=None, access_token=None, **kw):
        try:
            rfqObjSudo = self._rfq_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/my')

        values = self._rfq_get_page_view_values(rfqObjSudo, access_token, **kw)
        return request.render("odoo_vendor_portal.rfq_followup", values)



    @http.route(['/update/vendorprice/'], type='json', auth="user", methods=['POST'] , website=True)
    def vendor_update_price(self, rfqId, offerPrice, offerDate, offerNote, vendorUserId):
        context, env = request.context, request.env
        rfqModel = env['vendor.rfq']
        res = rfqModel.sudo().update_vendor_history(int(rfqId), float(offerPrice), offerDate, offerNote, vendorUserId)
        return {'rfqId' : rfqId}