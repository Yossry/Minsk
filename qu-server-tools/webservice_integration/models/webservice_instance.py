# Copyright 2019 Xavier Jimenez <xavier.jimenez@qubiq.es>
# Copyright 2019 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
from odoo.tools import ustr
import logging
_logger = logging.getLogger(__name__)
try:
    import traceback
    import xmlrpc.client
except (ImportError, IOError) as err:
    _logger.debug(err)


class Webservice(models.Model):
    _name = 'webservice.instance'
    _description = 'Webservice Instance'

    name = fields.Char(string='Name')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
    )

    webservice_active = fields.Boolean(string='Webservice active')
    ws_url = fields.Char(string='Webservice URL')
    ws_db = fields.Char(string='Webservice Database')
    ws_username = fields.Char(string='Webservice User')
    ws_password = fields.Char(string='Webservice Password')
    ws_type = fields.Selection(
        string='Connection Type',
        selection=[
            ('webservice.con.odoo', 'Odoo'),
            ('webservice.con.mysql', 'MySQL'),
            ('webservice.con.sqlserver', 'SQL Server'),
        ])

    mapper_ids = fields.One2many(
        comodel_name='webservice.mapper',
        inverse_name='webservice_id',
        string='Mapper',
        copy=True,
    )
    timeout = fields.Integer(string="Conection Timeout", default=300)

    connexion = []

    def close_connexion(self):
        if self.connexion:
            self.connexion = self._get_connexion_obj().close_connexion(self.connexion)

    def read_data(self, vals):
        ''''This function read data from db and return a dict'''
        con_obj = self._get_connexion_obj()
        #Check if there is a connection already
        self.connexion = self.connexion or con_obj.connect(self._get_access_data())
        data = con_obj.read_data(self.connexion, vals)
        return data

    def read_fields(self, table):
        "Reads the name of the columns of one table/model"
        con_obj = self._get_connexion_obj()
        self.connexion = self.connexion or con_obj.connect(
            self._get_access_data(), dictionary=False)
        fields = con_obj.read_fields(self.connexion, table)
        self.close_connexion()
        return fields

    def _get_connexion_obj(self):
        """Returns the connector model and connexion objects if
            connect == True
        """
        try:
            return self.env[self.ws_type]
        except Exception as err:
            raise UserError(str(err))

    def _get_access_data(self):
        return {
            'host': self.ws_url,
            'db': self.ws_db,
            'user': self.ws_username,
            'password': self.ws_password,
            'timeout': self.timeout or 300,
        }

    def check_connection_webservice(self):
        """Check the connection"""
        self.ensure_one()
        conn_obj = self._get_connexion_obj()
        data = self._get_access_data()
        conn_obj.check_connection(data)
