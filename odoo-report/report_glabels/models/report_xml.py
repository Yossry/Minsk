# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2004- Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _, registry
from openerp.exceptions import except_orm, Warning, RedirectWarning

from openerp.report import interface

import unicodecsv as csv
import os
import tempfile
import base64


import logging
_logger = logging.getLogger(__name__)


# http://jamesmcdonald.id.au/it-tips/using-gnubarcode-to-generate-a-gs1-128-barcode
# https://github.com/zint/zint

class report_xml(models.Model):
    _inherit = 'ir.actions.report.xml'

    ### Fields
    report_type = fields.Selection(selection_add=[('glabels', 'Glabels'),('glabels_rows', 'Glabels (rows)')])
    glabels_template = fields.Binary(string="Glabels template")
    label_count = fields.Integer(string="Count",default=1,help="One if you want to fill the sheet with new records, the count of labels of the sheet to fill each sheet with one record")
    col_name = fields.Char(string="Column",help="(Glabels rows) the name of name column for use in gLabels")
    col_value = fields.Char(string="Column",help="(Glabels rows) the name of value column for use in gLabels")


    @api.cr
    def _lookup_report(self, cr, name):
        if 'report.' + name in interface.report_int._reports:
            new_report = interface.report_int._reports['report.' + name]
        else:
            cr.execute("SELECT id, report_type,  \
                        model, glabels_template, label_count, col_name, col_value  \
                        FROM ir_act_report_xml \
                        WHERE report_name=%s", (name,))
            record = cr.dictfetchone()
            if record['report_type'] == 'glabels':
                template = base64.b64decode(record['glabels_template']) if record['glabels_template'] else ''
                new_report = glabels_report(cr, 'report.%s'%name, record['model'],template=template,count=record['label_count'])
            elif record['report_type'] == 'glabels_rows':
                template = base64.b64decode(record['glabels_template']) if record['glabels_template'] else ''
                new_report = glabels_report_rows(cr, 'report.%s'%name, record['model'],template=template,count=record['label_count'],col_name=record['col_name'],col_value=record['col_value'])
            else:
                new_report = super(report_xml, self)._lookup_report(cr, name)
        return new_report


class glabels_report(object):

    def __init__(self, cr, name, model, template=None,count=1,):
        _logger.info("registering %s (%s)" % (name, model))
        self.active_prints = {}

        pool = registry(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        name = name.startswith('report.') and name[7:] or name
        self.template = template
        self.model = model
        self.count = count
        try:
            report_xml_ids = ir_obj.search(cr, 1, [('report_name', '=', name)])
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, 1, report_xml_ids[0])
            else:
                report_xml = False
        except Exception, e:
            _logger.error("Error while registering report '%s' (%s)", name, model, exc_info=True)


    def create(self, cr, uid, ids, data, context=None):

        temp = tempfile.NamedTemporaryFile(mode='w+t',suffix='.csv')
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        glabels = tempfile.NamedTemporaryFile(mode='w+t',suffix='.glabels')
        glabels.write(base64.b64decode(data.get('template')) if data.get('template') else None or self.template)
        glabels.seek(0)

        pool = registry(cr.dbname)
        labelwriter = None
        for p in pool.get(self.model).read(cr,uid,ids):
            if not labelwriter:
                labelwriter = csv.DictWriter(temp,p.keys())
                labelwriter.writeheader()
            for c in range(self.count):
                labelwriter.writerow({k:isinstance(v, (str, unicode)) and v.encode('utf8') or str(v) for k,v in p.items()})
        temp.seek(0)
        res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name,temp.name,glabels.name))

        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        temp.close()
        glabels.close()
        return (pdf,'pdf')

class glabels_report_rows(object):

    def __init__(self, cr, name, model, template=None,count=1,col_name=None,col_value=None):
        _logger.info("registering %s (%s)" % (name, model))
        self.active_prints = {}

        pool = registry(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        name = name.startswith('report.') and name[7:] or name
        self.template = template
        self.model = model
        self.count = count
        self.col_name = col_name
        self.col_value = col_value
        try:
            report_xml_ids = ir_obj.search(cr, 1, [('report_name', '=', name)])
            if report_xml_ids:
                report_xml = ir_obj.browse(cr, 1, report_xml_ids[0])
            else:
                report_xml = False
        except Exception, e:
            _logger.error("Error while registering report '%s' (%s)", name, model, exc_info=True)


    def create(self, cr, uid, ids, data, context=None):

        temp = tempfile.NamedTemporaryFile(mode='w+t',suffix='.csv')
        outfile = tempfile.NamedTemporaryFile(mode='w+b',suffix='.pdf')
        glabels = tempfile.NamedTemporaryFile(mode='w+t',suffix='.glabels')
        glabels.write(base64.b64decode(data.get('template')) if data.get('template') else None or self.template)
        glabels.seek(0)

        pool = registry(cr.dbname)
        labelwriter = csv.DictWriter(temp,[h[self.col_name] for h in pool.get(self.model).read(cr,uid,pool.get(self.model).search(cr,uid,[]),[self.col_name])])
        labelwriter.writeheader()
        for c in range(self.count):
            #~ labelwriter.writerow({p[self.col_name]:isinstance(p[self.col_value], (str, unicode)) and p[self.col_value].encode('utf8') or p[self.col_value] or '' for p in pool.get(self.model).read(cr,uid,pool.get(self.model).search(cr,uid,[]),[self.col_name,self.col_value])])})
            labelwriter.writerow({p[self.col_name]: str(p[self.col_value]) if not str(p[self.col_value]) == '0.0' else '' for p in pool.get(self.model).read(cr,uid,pool.get(self.model).search(cr,uid,[]),[self.col_name,self.col_value], context=context)})
        temp.seek(0)
        res = os.system("glabels-3-batch -o %s -l -C -i %s %s" % (outfile.name,temp.name,glabels.name))
        outfile.seek(0)
        pdf = outfile.read()
        outfile.close()
        temp.close()
        glabels.close()
        return (pdf,'pdf')
