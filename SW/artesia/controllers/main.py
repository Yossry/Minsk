from odoo import http
from odoo.http import request


class WebsiteDemo(http.Controller):
    @http.route('/contactform_action', type='json', auth='public', website=True)
    def create_subscribe(self, **data):
        data = data and data['datas']
        res = dict()
        for d in eval(data):
            res[d.get('name')] = d.get('value')
        subscribe = request.env['crm.lead'].sudo().create({
            'name': res.get('name'),
            'phone': res.get('mobile'),
            'email_from': res.get('email'),
            'description': res.get('message'),
        })
        if not subscribe:
            return False
