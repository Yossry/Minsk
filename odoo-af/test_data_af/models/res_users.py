# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

import csv
import os
import tempfile

class ResUsers(models.Model):
    _inherit = "res.users"
    @api.model
    def create_users(self):
        a = ReadCSV("/usr/share/odoo-af/test_data_af/data/arbetsg/res.users.csv")
        self.create_user(a.parse())
    
    @api.model
    def create_user(self, rows):
        for row in rows:
            partner_id = self.env.ref("test_data_af.%s" % row['partner_id']).id
            row.update({'partner_id' :  partner_id}) 
            _logger.info("%s" % row['partner_id'])       
            _logger.info("creating row %s" % row)
            self.env['res.users'].create(row)


    #create a record using data from csv

class ReadCSV(object):
    def __init__(self, path):     
        try:
            rows = []
            f = open(path)
            f.seek(0)
            reader = csv.DictReader(f,delimiter=",")
            for row in reader:
                rows.append(row)
            f.close()
            self.data = rows
        except IOError as e:
            _logger.error(u'Could not read CSV file')
            raise ValueError(e)
        if not list(self.data[0].keys()) == ['external_id', 'login', 'password', 'partner_id']:
            _logger.error(u'Row 0 was looking for "id", "login", "password", "partner_id"')
            raise ValueError("Wrong format, expected format: ['external_id', 'login', 'password', 'partner_id'], seems like we're getting: %s" % list(self.data[0].keys()))

    def parse(self):
        a = CSVIterator(self.data,len(self.data),['external_id', 'login', 'password', 'partner_id'])
        rows = []
        while a.hasNext():
            _logger.info("appending row %s" % a.getRow())
            rows.append(a.getRow())
            a.next()
        return rows


class CSVIterator(object):
    def __init__(self, data, nrows, header, header_row=1):
        self.nrows = nrows
        self.row = 0
        self.data = data
        self.rows = nrows - 2
        self.header = header

    def next(self):
        if self.hasNext():
            self.row += 1

    def hasNext(self):
        return self.row <= self.nrows -1

    def getRow(self):
        r = list(self.data[(self.row)].values())      
        return {self.header[n]: r[n] for n in range(len(self.header))}
    
