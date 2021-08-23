# Copyright 2019 Jesus Ramoneda <jesus.ramonedae@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, _, api
from odoo.exceptions import Warning, ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)
try:
    import traceback
    import xmlrpc.client
except (ImportError, IOError) as err:
    _logger.debug(err)
try:
    import mysql.connector
    from mysql.connector import errorcode
except (ImportError, IOError) as err:
    _logger.debug(err)
try:
    import pymssql
except (ImportError, IOError) as err:
    _logger.debug(err)


class WebserviceConnector(models.AbstractModel):
    _name = 'webservice.connector'
    _description = "Webservice Conector"

    def connect(self, params, **kargs):
        pass

    def close_connection(self, connexion):
        return None

    def check_connection(self, **kargs):
        raise Warning(_('The connexion was succesfull!'))

    def read_data(self, connexion, vals, **kargs):
        pass

    def read_fields(self, conn, table):
        pass
    def prepare_domain(self, domain):
        """It recives a domain of Odoo [(f,o,v)] and will return
        a domain adapted to the connexion source"""
        pass


class WeberviceSQLSERVERConnector(models.AbstractModel):
    _name = 'webservice.con.sqlserver'
    _inherit = 'webservice.connector'
    _description = "Webservice SQL SERVER Conector"

    @api.model
    def connect(self, params, **kargs):
        try:
            conn = pymssql.connect(
                params.get('host', ''),
                params.get('user', ''),
                params.get('password', ''),
                params.get('db', ''), params.get('timeout', 300),
            )
            cursor = conn.cursor(as_dict=kargs.get('dictionary', True))
            return [conn, cursor]

        except pymssql.DatabaseError as err:
            raise Warning(str(err))

    def close_connexion(self, conn):
        try:
            conn[0].close()
            conn[1].close()
            return None
        except:
            _logger.info(_('Connection Close Failed'))
            return None

    @api.model
    def check_connection(self, params):
        try:
            conn = self.connect(params)
            self.close_connexion(conn)
        except Exception as err:
            _logger.info(str(err))
            raise UserError(_("Connection Failed! %s" % str(err)))
        return super(WeberviceSQLSERVERConnector, self).check_connection()

    def read_fields(self, conn, table):
        conn[1].execute("""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '%s'""" % table)
        data = conn[1].fetchall()
        return [x[0] for x in data]

    def prepare_domain(self, values):
        if not values:
            return ""
        domain = "WHERE "
        for x in values:
            domain += "%s%s'%s' " % (x[0], x[1], x[2])
        return domain

    def read_data(self, conn, values, **kargs):
        conn[1].execute("""SELECT %s FROM %s %s
        """ % (', '.join(values['fields']), values['table'],
               self.prepare_domain(values['domain'])))
        return conn[1].fetchall()


class WeberviceMySQLConnector(models.AbstractModel):
    _name = 'webservice.con.mysql'
    _inherit = 'webservice.connector'
    _description = "Webservice Mysql Connector"

    @api.model
    def connect(self, params={}, **kargs):
        try:
            conn = mysql.connector.connect(
                user=params.get('user', ''),
                password=params.get('password', ''),
                port=params.get('port', ''),
                host=params.get('host', ''),
                database=params.get('db', ''),
                connect_timeout=params.get('timeout', 300),
            )
            cursor = conn.cursor(dictionary=kargs.get('dictionary', True))
            return [conn, cursor]
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise Warning(_("User or password are incorrect"))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise Warning(
                    _("Database not found")
                )
            else:
                raise Warning(err)

    def close_connexion(self, connexion):
        try:
            connexion[0].close()
            connexion[1].close()
            return None
        except Exception:
            _logger.info(_('Connection Close Failed'))
            return None

    @api.model
    def check_connection(self, params):
        connexion = self.connect(params)
        self.close_connexion(connexion)
        return super(WeberviceMySQLConnector, self).check_connection()

    def read_fields(self, conn, table):
        conn[1].execute("""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '%s'""" % table)
        return conn[1].fetchall


class WeberviceOdooConnector(models.AbstractModel):
    _name = 'webservice.con.odoo'
    _inherit = 'webservice.connector'
    _description = "Webservice Odoo Conector"

    @api.model
    def connect(self, params={}, **kargs):
        try:
            common = xmlrpc.client.ServerProxy(
                '{}/xmlrpc/2/common'.format(params['host'])
            )
            common.version()
            uid = common.authenticate(
                params['db'], params['user'], params['password'], {}
            )
            if not uid:
                raise Warning(_("Login/password not valid!"))
            models = xmlrpc.client.ServerProxy(
                '{}/xmlrpc/2/object'.format(params['host']))
            return [models, params['db'], uid, params['password']]
        except Exception as er:
            raise Warning(_("Connection with Odoo Failed \n %s" % str(er)))

    def close_connexion(self, connexion):
        conexion = None
        return conexion

    def check_connection(self, params):
        connexion = self.connect(params)
        self.close_connexion(connexion)
        return super(WeberviceOdooConnector, self).check_connection()

    def read_fields(self, conn, table):
        try:
            field_list = conn[0].execute_kw(
                conn[1], conn[2], conn[3], table,
                'fields_get', [],
                {'attributes': ['type']})
            return field_list.keys()
        except Exception:
            raise UserError(_("Cannon Read Fields Names"))

    def prepare_domain(self, domain):
        """return [[f,o,v]]"""
        prepared_domain = []
        for e in domain:
            if type(e) is tuple:
                prepared_domain.append(list(e))
            else:
                prepared_domain.append(e)
        return prepared_domain

    def read_data(self, conn, values, **kargs):
        domain = self.prepare_domain(values['domain'])
        data = conn[0].execute_kw(
            conn[1], conn[2], conn[3], values['table'],
            'search_read', [domain], {'fields': values['fields']})
        return data
