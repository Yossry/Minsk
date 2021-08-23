# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
import json
from .  import client

_logger = logging.getLogger(__name__)
lista=[]

class tracksController(http.Controller):
    #parameter = {"CAT_CL":'2017-10-09 16:47:55',"CAT_PR":'-'}
    @http.route('/xltrack/cancelacion', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def lxtrackcancelacion(self, **post):
        print('hola')
        bd=post.get('BD')
        odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname=bd, port=8069,
                                 debug=True)
        odoo.ServerInfo()
        user = 'admin'
        passw = 'pascualadmin'
        odoo.Authenticate(user, passw)
        print(odoo.Authenticate(user, passw))
        if odoo.Authenticate(user, passw) is not False:
            valor=post.get('ORDEN')
            print(valor)
            order = odoo.SearchRead('sale.order', [('name', '=', valor)], ['id'])
            print('ORDENEESSSSSSSSSSSS')
            print(order)
            if order is not None:
                for p in order:
                    lista.append(p['id'])
                    print('hayo orden')
                    print(lista)
                    odoo.Write('sale.order', lista, {'state': "cancel"})
                    json_exitoso = {
                        'data': {
                            'message': {
                                'type​': 'Succesful'
                            }
                        }
                    }
                    return json.dumps(json_exitoso)
            else:
                json_error = {
                    'data': {
                        'message':{
                            'type': 'ERROR'
                        }
                    }
                }
                return json.dumps(json_error)
        else:
            return "ERRROR"
        return json.dumps({'data': 'Existe un problema en la API :o'})