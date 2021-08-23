# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsiteSubscribeCreate(http.Controller):

    @http.route('/subscribe_action', type='json', auth='public', website=True)
    def create_subscribe(self, **data):
        data = data and data['datas']
        res = dict()
        for d in eval(data):
            res[d.get('name')] = d.get('value')
        subscribe = request.env['website.subscribe'].sudo().create({
            'name': res.get('subsemail'),
        })
        if not subscribe:
            return False
