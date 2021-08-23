from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WebserviceMapperFields(models.Model):
    _name = 'webservice.mapper.fields'
    _description = 'Webservice Mapper Fields'

    odoo_field = fields.Many2one(
        comodel_name='ir.model.fields',
        required=True,
        help="Table name or model name if the source is odoo")
    odoo_relation = fields.Char(related="odoo_field.relation")
    field_type = fields.Selection(related="odoo_field.ttype")
    source_field = fields.Char(help="Field name from the source")
    dependence_ref_code = fields.Char(index=True, copy=False)
    dependence_id = fields.Many2one(
        comodel_name='webservice.mapper',)
    webservice_mapper_id = fields.Many2one(
        comodel_name='webservice.mapper',
        string='Webservice Mapper',
        copy=True
    )
    state_valid = fields.Selection(
        string='Valid',
        selection=[('not_check', 'Not Checked'),
                   ('valid', 'Valid'),
                   ('not_valid', 'Not Valid')],
        default='not_check',
        compute="_compute_state_valid",
        store=True)

    @api.depends('source_field', 'odoo_field')
    def _compute_state_valid(self):
        self.state_valid = False

    unique = fields.Boolean(help="Is a unique field?")
    map_values = fields.Char(string='Map Values',
                             help="Transform values recivied")
    create_method = fields.Selection(
        selection=[('before', 'Before'),
                   ('together', 'Together'),
                   ('after', 'After')],
        default='together', compute="_compute_create_method",
        store=True, readonly=False)
    search_operator = fields.Selection(
        selection=[('&', 'AND'), ('|', 'OR')], default="|")
    sequence = fields.Integer(default=10)

    @api.depends('field_type')
    def _compute_create_method(self):
        for rec in self:
            if rec.field_type in ["one2many", "many2many"]:
                rec.create_method = 'together'

    def get_company_domain(self):
        """This function returns company domain if
           the model has a company_id field"""
        self.ensure_one()
        model_obj = self.env['ir.model'].search([
                ('model', '=', self.odoo_field.relation)
            ])
        if not model_obj or not self.webservice_mapper_id.webservice_id:
            return []
        if model_obj.field_id.filtered(
             lambda o: o.name == 'company_id'):
            company_id = self.webservice_mapper_id.webservice_id.company_id
            return [("company_id", "=", company_id.id)]
        return []

    def get_field_domain(self, value):
        op = 'in' if type(value) is list else '='
        return [(self.odoo_field.name, op, value)]

    def transform_data(self, val):
        """Recive, transform and return data accordingly
         with the map_values field"""
        self.ensure_one()
        try:
            if not self.map_values:
                return val
            transfomer = eval(self.map_values)
            if transfomer:
                return transfomer.get(val, False) or val
            else:
                return val
        except Exception:
            raise UserError(_("Map values of %s are incorrect") %
                            self.odoo_field.name)
        return val

    @api.multi
    def create_dependence(self):
        rec_list = []
        for rec in self.filtered(lambda x: x.odoo_relation and not
                                 x.dependence_id):
            rec.dependence_id = rec._create_dependence()
            rec_list.append(rec.dependence_id)
        return rec_list

    def _create_dependence(self):
        """This functions create a new mapper if there are dependences
        in the current field Returns a record"""
        try:
            parent_id = self.webservice_mapper_id
            model_obj = self.env['ir.model'].search([
                ('model', '=', self.odoo_field.relation)
            ])
            mapper_obj = self.env['webservice.mapper'].search([
                ('odoo_model', '=', model_obj.id),
                ('webservice_id', '=', parent_id.webservice_id.id),
            ])
            if mapper_obj:
                mapper_obj.write({'dep_field_ids': [(4, self.id)]})
                return mapper_obj
            values = {
                'name': model_obj.name,
                'active': parent_id.active,
                'source_model': model_obj.model,
                'odoo_model': model_obj.id,
                'dep_field_ids': [(4, self.id)],
                'webservice_id': parent_id.webservice_id.id,
                'update': parent_id.update,
                'create_active': parent_id.create_active,
            }
            return mapper_obj.create(values)
        except Exception as e:
            raise UserError("Error when creating dependence mappers:\n %s"
                            % str(e))

    def search_record(self, value, many2many, search_name=True):
        """Search relation by name or by old id
        return the record or False"""
        try:
            model_obj = self.env[self.odoo_relation]
        except Exception:
            raise UserError(_("Model %s not found!") % self.odoo_relation)
        if 'x_old_id' in model_obj._fields:
            if many2many:
                domain = [('x_old_id', 'in', value)]
            else:
                domain = [('x_old_id', '=', value[0])]
            rec = self.env[self.odoo_relation].search(domain)
            if rec and many2many:
                return rec
            elif len(rec) == 1:
                return rec
        field = True
        if not search_name or many2many:
            return False
        if 'display_name' in model_obj._fields:
            # This can slow the process
            # Display name is a field computed we cannot search
            # with the ORM
            domain = []
        elif 'name' in model_obj._fields:
            domain = [('name', '=', value[1])]
        else:
            field = False
        if field:
            rec = self.env[self.odoo_relation].search(domain)
            if not domain and rec:
                rec = rec.filtered(lambda x: x.display_name == value[1])
            if len(rec) == 1:
                return rec

    def open_mapper(self):
        self.ensure_one()
        if not self.dependence_id:
            return
        action = self.env.ref(
            'webservice_integration.webservice_mapper_action_form')
        action['res_id'] = self.dependence_id.id
        return action
