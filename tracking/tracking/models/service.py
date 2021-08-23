#!/usr/bin/env python
import web
from . import client
import datetime


odoo = client.OdooClient(protocol='xmlrpc', host='localhost', dbname='odoo', port=8069, debug=True)
odoo.ServerInfo()
odoo.Authenticate('admin', 'admin')
urls = (
    '/xltrack?', 'clientes_filtrados',
)

app = web.application(urls, globals())

class list_users:
    def GET(self):
        fecha_clientes = odoo.SearchRead('res.partner', [('active', '=', True)], ['write_date'])
        sorted_date = sorted(fecha_clientes, key=lambda i: i['write_date'], reverse=True)
        output=''
        l = []
        bol= False
        for i in sorted_date:
            insert = ''
            if bol==False:
                l.append(i['write_date'])
                bol=True
            if  i['write_date'] not in l:
                print("if : %s" % l)
                l.append(i['write_date'])
                fecha_inicio = i['write_date'] + '.0'
                fecha_fin = i['write_date'] + '.99999999999'
                cont = odoo.SearchCount('res.partner',
                                        [('write_date', '>=', fecha_inicio), ('write_date', '<=', fecha_fin)])
                # print(cont)
                output = output + '\n'+ str(i['write_date']) + ' ' + str(cont) + ':['
                partners = odoo.SearchRead('res.partner',
                                           [('write_date', '>=', fecha_inicio), ('write_date', '<=', fecha_fin)],
                                           ['name', 'display_name', 'website', 'function', 'phone', 'mobile', 'email',
                                            'active'])
                print("Partnerssss %s"%len(partners))
                for p in partners:
                    if str(p['active'])== False:
                        activo=0
                    else: activo=1
                    insert = insert + '\n' + "INSERT OR REPLACE INTO CLIENTE(id,id_servidor,nombre,nombre_comercial,sitio_web,puesto_trabajo,tel,movil,fax,email,id_precio_lista,active) VALUES(" + str(
                        p['id']) + ",?,'" + str(p['name']) + "','" + str(p['display_name']) + "','"+ str(
                        p['website']) + "','" + str(p['function']) + "','" + str(p['phone']) + "','" + str(
                        p['mobile']) +"',,'" + str(p['email']) + "',," + str(activo) + ");"
                output += insert +']'+ '\n\n'


        return output

class clientes_filtrados:
    def GET(self):
        a = web.input()
        insert=''
        output=""
        print("valores fecha inicio %s" %  datetime.datetime.now())
        fecha_inicio =a.CAT_CL+'.0'
        fecha_fin=datetime.datetime.now()
        print("fecha inicio %s"% fecha_inicio)
        print("fecha ifn %s" % fecha_fin)
        cont = odoo.SearchCount('res.partner',
                                [('write_date', '>=',fecha_inicio)])
        output = output + '\n'+'clientes = {' + '\n'+'\t "'+a.CAT_CL + '" ' + str(cont) +':['
        partners = odoo.SearchRead('res.partner',
                                  [('write_date', '>=', fecha_inicio)],
                                  ['name', 'display_name', 'website', 'function', 'phone', 'mobile', 'email',
                                   'active'])
        print("Partnerssss %s" % len(partners))
        for p in partners:
            if str(p['active']) == False:
                activo = 0
            else:
                activo = 1
            insert = insert + '\n\t\t' + "INSERT OR REPLACE INTO CLIENTE(id,id_servidor,nombre,nombre_comercial,sitio_web,puesto_trabajo,tel,movil,fax,email,id_precio_lista,active)"+"\n\t\t VALUES(" + str(
                p['id']) + ",?,'" + str(p['name']) + "','" + str(p['display_name']) + "','" + str(
                p['website']) + "','" + str(p['function']) + "','" + str(p['phone']) + "','" + str(
                p['mobile']) + "',,'" + str(p['email']) + "',," + str(activo) + ");"
        val= insert+ '\n\t' + ']'
        output += val+'\n}'

        return output



if __name__ == "__main__":
    app.run()