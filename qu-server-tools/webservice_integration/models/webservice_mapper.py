# Copyright 2019 Jesus Ramoneda <jesus.ramonedae@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.addons.queue_job.job import job
from odoo.tools import pycompat
from odoo.exceptions import ValidationError, UserError
import io
import random
import base64
import logging
_logger = logging.getLogger(__name__)


class WebserviceMapper(models.Model):
    _name = 'webservice.mapper'
    _description = 'Webservice Mapper'
    _order = 'sequence, id'

    name = fields.Char(required=1)
    active = fields.Boolean()
    webservice_id = fields.Many2one(
        comodel_name='webservice.instance',
        string='Webservice',
    )
    sequence = fields.Integer(default=10)
    ref_code = fields.Char(index=True, copy=False)
    unique_source_field = fields.Char()
    sync_ids = fields.Char(string="Sync IDS",
                           help="select specific id or [ids] for sync")
    dep_field_ids = fields.One2many(comodel_name='webservice.mapper.fields',
                                    inverse_name='dependence_id')
    dep_mapper_id = fields.Many2one(
        comodel_name='webservice.mapper',
        related='dep_field_ids.webservice_mapper_id')
    source_model = fields.Char(
        help="Table name or model name if the source is odoo", required=1)
    odoo_model = fields.Many2one(
        comodel_name='ir.model',
        help="Table name or model name if the source is odoo",
        required=True)
    odoo_model_name = fields.Char(related='odoo_model.model')
    mapper_fields_ids = fields.One2many(
        comodel_name='webservice.mapper.fields',
        inverse_name='webservice_mapper_id',
        string='Mapper Fields',
        copy=True)
    is_valid_fields = fields.Boolean(
        help="True when all the mapped fields are in green",
        compute="_compute_is_valid_field",
        store=True
    )

    @api.depends('mapper_fields_ids.state_valid')
    def _compute_is_valid_field(self):
        for rec in self:
            rec.is_valid_fields = bool(not self.mapper_fields_ids.filtered(
                lambda x: x.state_valid != 'valid'))

    search_field = fields.Char(help="""Fields used for search and use records
        in the current odoo database""")
    company_field = fields.Char(help="Column name for company_id",
                                compute="_compute_company_field",
                                store=True,
                                readonly=False)
    search_domain = fields.Char(help="""Domain used for search and use records
        in the source odoo database""")
    method_calls = fields.Text(
        help="""Separate with ; the list of the method to use
         after create the object""")
    update = fields.Boolean(
        help="""When is activated the record will be overwrite
         in case that it already exist""",
        default=True)
    create_active = fields.Boolean(
        help="When is activated the record will be created", default=True)
    hide_create_unique_field = fields.Boolean()
    debug_mode = fields.Boolean(help=_("It will display technical information"
                                       " in the console"))

    result = fields.Text(string='')

    def get_ref_code(self):
        """Write a unique ref code for exports/imports"""
        if not self.ref_code:
            num_2 = random.randint(10, 99)
            num = random.randint(1000, 9999)
            ref_code = '%s_%s_%s' % (self.odoo_model_name, num_2, num)
            self.write({'ref_code': ref_code})
        return self.ref_code

    def export_mappers(self):
        """ Creates the files and open the wizard to download them """
        export_wiz = self.env['export.webservice.mapper'].create({})
        export_files = self.env['export.webservice.file']
        for rec in self:
            file_data, file_name = rec.get_export_data()
            export_wiz.file_ids += export_files.create({
                'file_name': file_name,
                'file_data': file_data,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Mappers',
            'res_model': 'export.webservice.mapper',
            'res_id': export_wiz.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def get_export_data(self):
        """ Generates the data and create the file to export """
        self.ensure_one()
        fp = io.BytesIO()
        exporter = self.env['export.webservice.mapper']
        writter = pycompat.csv_writer(fp, quoting=1)
        writter.writerow(exporter._columns_mapper)
        writter.writerow(exporter.get_export_mapper_data(self))
        writter.writerow(exporter._columns_fields)
        for field in self.mapper_fields_ids:
            writter.writerow(exporter.get_export_field_data(field))
        return base64.encodestring(fp.getvalue()), self.name + '.csv'

    def format_get_dep_fields(self):
        vals = [
            x.get_ref_code()
            for x in self.dep_field_ids.mapped('webservice_mapper_id')
        ]
        return '/'.join(vals)

    def get_company_domain(self):
        if self.company_field:
            return [(self.company_field, "=", self.webservice_id.company_id.id)
                    ]
        return []

    @api.depends('odoo_model')
    def _compute_company_field(self):
        for rec in self:
            if rec.odoo_model.field_id.filtered(
                    lambda o: o.name == 'company_id'):
                rec.company_field = "company_id"
            else:
                rec.company_field = ""

    @api.onchange('odoo_model_name')
    def _onchange_odoo_model_name(self):
        if self.odoo_model_name:
            self.source_model = self.odoo_model_name
        else:
            self.source_model = ''

    def create_unique_field(self):
        """Create a new field in the model called x_old_id that will store
           the id of the source object
        """
        self.ensure_one()
        field_obj = self.env['ir.model.fields']
        field_obj = field_obj.search([
            ('name', '=', 'x_old_id'),
            ('model_id', '=', self.odoo_model.id),
        ])
        if not field_obj:
            field_obj = field_obj.sudo().create({
                'name': 'x_old_id',
                'field_description': 'Old ID',
                'model': self.odoo_model_name,
                'model_id': self.odoo_model.id,
                'ttype': 'integer',
                'store': True,
                'index': True,
                'state': 'manual'
            })
        map_field_obj = self.env['webservice.mapper.fields']
        if not map_field_obj.search([
            ('webservice_mapper_id', '=', self.id),
            ('odoo_field', '=', field_obj.id),
        ]):
            map_field_obj.create({
                'odoo_field': field_obj.id,
                'webservice_mapper_id': self.id,
                'source_field': 'id',
                'unique': True,
                'state_valid': 'valid'
            })
        self.hide_create_unique_field = True

    def _check_mapped_fields(self, field_list):
        """Check if the fields given are the same in the configuration"""

        all_valid = True
        unique_fields = self._get_unique_fields()
        for mapped_field in self.mapper_fields_ids:
            if mapped_field.source_field in field_list:
                mapped_field.state_valid = 'valid'
            elif (not mapped_field.source_field
                  and mapped_field.odoo_field.name in field_list):
                mapped_field.write({
                    'state_valid':
                    'valid',
                    'source_field':
                    mapped_field.odoo_field.name,
                })
            elif (mapped_field.odoo_field.name[-3:] == '_id'
                  and mapped_field.odoo_field.name[:-3] in field_list):
                mapped_field.write({
                    'state_valid':
                    'valid',
                    'source_field':
                    mapped_field.odoo_field.name[:-3],
                })
            else:
                mapped_field.state_valid = 'not_valid'
                all_valid = False
            if mapped_field.odoo_field.name in unique_fields:
                mapped_field.unique = True
        return all_valid

    def _get_unique_fields(self):
        model_obj = self.env[self.odoo_model_name]
        unique_fields = ['id', 'x_old_id']
        for cons in model_obj._sql_constraints:
            if 'uniq' in cons[0]:
                try:
                    unique_fields.append(cons[0].split('_')[0])
                except Exception:
                    pass
        return unique_fields

    def check_mapped_fields(self):
        self.ensure_one()
        if not self.is_valid_fields:
            self.is_valid_fields = self._check_mapped_fields(
                self.webservice_id.read_fields(
                    table=self.source_model))
        # self.check_dependences_fields()
        return self.is_valid_fields

    # TODO check bug with infinite bucle
    def check_dependences_fields(self):
        self.ensure_one()
        all_valid = True
        for field_dep in self.mapper_fields_ids.filtered(
                lambda x: x.dependence_id and not
                x.dependence_id.is_valid_fields):
            if not field_dep.dependence_id.check_mapped_fields():
                all_valid = False
                field_dep.state_valid == "not_valid"
        return all_valid

    def create_dependences(self):
        for rec in self:
            dep_list = rec.mapper_fields_ids.create_dependence()
            for dep in dep_list:
                dep.fill_required_fields()

    def fill_required_fields(self):
        for rec in self:
            if not rec.odoo_model:
                raise UserError(_('You must select a Odoo Model'))
            current_fields = rec.mapper_fields_ids.mapped('odoo_field').mapped(
                'name')
            required_fields = rec.odoo_model.field_id.filtered(
                lambda f: f.required and 'company_id' not in f.name)
            mapper_field_obj = self.env['webservice.mapper.fields']
            for field in required_fields:
                if current_fields and field.name in current_fields:
                    continue
                rec.mapper_fields_ids += mapper_field_obj.create(
                    {'odoo_field': field.id})
            rec.check_mapped_fields()

    def get_mapped_fields(self, for_search=False):
        """Return a dict with k=source field and v= odoo field"""
        if for_search:
            return list(map(lambda x: x.source_field or x.odoo_field.name,
                            self.mapper_fields_ids))
        res = {}
        for field in self.mapper_fields_ids:
            field.source_field = field.source_field or field.odoo_field.name
            res.update({field.source_field: field.odoo_field.name})
        return res

    def _get_search_domain(self):
        if self.search_domain:
            try:
                domain = eval(self.search_domain)
            except Exception:
                raise ValidationError(_("Error Validating Search Domain"))
            if type(domain) is not list:
                raise ValidationError(_("Error Validating Search Domain"))
            return domain

    def prepare_read_values(self, table, fields, domain):
        """This functions return a dict with the following keys
           table: str name of the table to search
           fields: list of the fields
           domain: domain written in source language
        """
        return {
            'table': table,
            'fields': fields,
            'domain': domain
        }

    def get_data_for_sync(self):
        """This function reads only the unique field from the source table,
            then iterates from those unique fields in order to read
            the rest of the mapped information one by one
        """
        for rec in self.filtered('active'):
            if not rec.check_mapped_fields():
                raise UserError(
                    _("There are invalid fields for mapper %s,"
                        " check it out") % rec.name)
            # Preparing domain for search data in external source
            domain = []
            add_domain = rec._get_search_domain()
            if add_domain:
                domain.append(add_domain)
            # Only the unique field is readed
            read_vals = rec.prepare_read_values(
                table=rec.source_model,
                fields=[rec.unique_source_field or 'id'], domain=domain)
            res_list = rec.webservice_id.read_data(read_vals)
            for res in res_list:
                rec.with_delay().sync_data(
                    res[rec.unique_source_field or 'id'])
        return {}

    @api.multi
    def action_sync_data(self):
        for rec in self:
            if not rec.check_mapped_fields():
                raise UserError(
                    _("There are invalid fields for mapper %s,"
                        " check it out") % rec.name)
            rec.sync_data()
        return {}

    @job
    def sync_data(self, res_id=False, odoo_rec=False, create_method='before'):
        """Writting data for %s""" % self.name
        """This functions controls the operations of reading and writting
        ---INPUTS---
        res_id: unique value of the source db
        odoo_rec: related record in Odoo DB
        created_method: param used in writting
        ---OUTPUTS---
        record_list: list of records in Odoo
        """
        self.ensure_one()
        if not self.active:
            return
        record_list = []
        # If we don't pass the res_id it is get from sync_ids field
        if not res_id:
            try:
                res_id = eval(self.sync_ids)
                if type(res_id) is not int and type(res_id) is not list:
                    res_id = False
            except Exception:
                res_id = False
        # Reading Data
        data_list, odoo_rec = self.read_data(res_id, odoo_rec)
        # If the record already exits and don't want to update
        if odoo_rec and not data_list:
            odoo_rec = odoo_rec if type(odoo_rec) is list else [odoo_rec]
            for rec in odoo_rec:
                record_list.append(rec)
        # Write the data. If data_list is empty its means update == False
        # or the source db is empty
        for data in data_list:
            rec_id = self.write_data(data, odoo_rec, create_method)
            if rec_id:
                record_list.append(rec_id)
        return record_list

    def read_data(self, res_id=False, odoo_rec=False):
        """This function read the mapped data from source database search if
        the record already exists in the current database:
        --INPUTS--
        rec_id: list or int represent unique value for search.
        odoo_rec: record from current db
        --OUTPUTS--
        data_list: list of dicts from souce db data
        odoo_rec: list of records the current db
        """
        self.ensure_one()
        if odoo_rec and not self.update:
            return [], odoo_rec
        # Init Variables
        domain, op = [], "="
        # Get odoo model
        model_obj = self.env[self.odoo_model.model].sudo()
        # Reading in current databases
        # If res_id is set search this record in current odoo  and source odoo
        if res_id:
            res_id = res_id[0] if type(res_id) is list and len(
                res_id) == 1 else res_id
            search_field = self.search_field or 'x_old_id' in \
                model_obj._fields and 'x_old_id'
            if not odoo_rec and search_field:
                # Set Domain for Current Odoo DB
                domain += self.get_company_domain()
                op = 'in' if type(res_id) is list else '='
                domain = [(search_field, op, res_id)]
                odoo_rec = model_obj.search(domain)
                if odoo_rec and not self.update:
                    return [], odoo_rec
            # Set Domain for Source Odoo DB
            domain = [(self.unique_source_field or 'id', op, res_id)]
        elif self.search_domain:
            domain = eval(self.search_domain)
        read_fields = self.get_mapped_fields(for_search=True)
        read_vals = self.prepare_read_values(
            table=self.source_model, fields=read_fields, domain=domain)
        data_list = self.webservice_id.read_data(read_vals)
        self.result = '--DATA READ--\n %s' % str(data_list)
        return data_list, odoo_rec

    def write_data(self, data_read, odoo_rec=False, create_method='before'):
        """This function write data for the model and return the record
            res_id = id in source, odoo_rec = rec in current odoo
            record_list and data are use for reset the values
            in recursive call
            --- RETURN ---
            if create_method == together : return dict with data_write
            else: return odoo_rec
        """
        if not data_read:
            return False
        # Init Variables
        domain, data_write = [], {}
        model_obj = self.env[self.odoo_model.model].sudo()
        # Get all Mapped Fields related with other models
        dependences_ids = self.mapper_fields_ids.filtered(
            lambda x: x.odoo_relation)
        for dependence in dependences_ids:
            field_name = dependence.source_field
            # Continue if we don't have source data for the dependence
            if not data_read.get(field_name):
                continue
            is_o2m = dependence.odoo_field.ttype in ["one2many", "many2many"]
            # Search record values in the current database
            res_values = data_read[field_name]
            # If there is a mapper for the dependence set up
            if dependence.dependence_id:
                if is_o2m:
                    # Recursive sync data for get a odoo record
                    #  or dict with data if create_method == together
                    depen_recs = dependence.dependence_id.sync_data(
                        res_id=res_values,
                        create_method=dependence.create_method)
                    if not depen_recs:
                        continue
                    depen_vals = []
                    # Separate Odoo record from data values
                    dict_values = [x for x in depen_recs if type(x) is dict]
                    record_values = [
                        x for x in depen_recs if x not in dict_values
                    ]
                    if record_values:
                        depen_vals.append(
                            (6, 0, [x.id for x in record_values]))
                        if dependence.unique:
                            domain.append((dependence.odoo_field.name, 'in',
                                           [x.id for x in record_values]))
                    depen_vals += [(0, 0, val) for val in dict_values]
                else:
                    # res_values[0] because in many2one field
                    # the API of odoo returns a tuple (id, 'display_name')
                    value = dependence.dependence_id.sync_data(
                        res_id=res_values[0])
                    if not value or not value[0]:
                        continue
                    depen_vals = value[0].id
                    if dependence.unique:
                        domain.append(
                            (dependence.odoo_field.name, '=', depen_vals))
            else:
                # If there isn't a mapper set up
                # search in the current database by display_name or x_old_id
                # Is usefull for models like currency, taxes, accounts etc..
                depen_ids = dependence.search_record(
                    value=res_values, many2many=is_o2m, search_name='odoo' in
                    self.webservice_id.ws_type)
                if depen_ids:
                    depen_vals = ([(6, 0, [x.id for x in depen_ids])]
                                  if is_o2m else depen_ids.id) \
                        if depen_ids else False
                else:
                    depen_vals = False
            data_write.update({dependence.odoo_field.name: depen_vals})
            data_read.pop(field_name)
        data_write_after = {}
        # Prepare a dict with not relational values
        # Also prepare a domain with unique values
        OR_domain = []
        for field_id in self.mapper_fields_ids:
            # Not value for the field found in the source DB
            if field_id.source_field not in data_read.keys():
                continue
            value = data_read[field_id.source_field]
            if (not value and field_id.odoo_field.ttype not in
                    ['boolean', 'integer', 'float']):
                continue
            # Add field to the domain
            if field_id.unique:
                if field_id.search_operator == '|':
                    OR_domain += field_id.get_field_domain(value)
                else:
                    domain += field_id.get_field_domain(value)
            # Separate dicts between after and together or before
            # Also transform data if map is set
            if field_id.create_method == "after":
                data_write_after.update({
                    field_id.odoo_field.name:
                    field_id.transform_data(value)
                })
            else:
                data_write.update({
                    field_id.odoo_field.name:
                    field_id.transform_data(value)
                })
        # Fill with company
        if self.company_field:
            data_write.update(
                {self.company_field: self.webservice_id.company_id.id})
            domain += bool(domain) and self.get_company_domain() or []
        # ['|' * len OR domain  + domain]
        domain = ['|' for x in range(len(OR_domain) - 1)] + OR_domain + domain
        found = False
        # Delete None values
        data_write = {k: v for k, v in data_write.items() if v is not None}
        # Get Default Values and adds to data write
        data_write = {**model_obj.default_get(data_write), **data_write}
        if self.debug_mode:
            # Avoid binary fields in the resut
            binary_field = self.mapper_fields_ids.filtered(
                lambda x: x.field_type == "binary")
            data_debug = data_write.copy()
            if binary_field:
                for bf_name in binary_field.mapped('odoo_field'). \
                        mapped('name'):
                    if data_debug.get(bf_name):
                        del data_debug[bf_name]
            self.result += "\n----DATA WRITE----\n%s" % str(data_debug)
        # Update Logic
        if not odoo_rec and domain:
            if self.debug_mode:
                self.result += "SEARCH DOMAIN:  %s\n" % domain
            odoo_rec = model_obj.search(domain)
        if odoo_rec:
            if self.update:
                odoo_rec.sudo().write(data_write)
        else:
            if not self.create_active:
                return
            if create_method == 'together':
                # Returns a dict with data
                return data_write
            odoo_rec = model_obj.create(data_write)
        if self.method_calls:
            if not found or (found and self.update):
                for method in self.method_calls.split(';'):
                    try:
                        getattr(odoo_rec, method)()
                    except Exception as err:
                        _logger.info('Error with calling method %s' % err)
        if data_write_after:
            odoo_rec.sudo().write(data_write_after)
        return odoo_rec[0]
