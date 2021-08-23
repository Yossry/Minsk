## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
import logging
from hashlib import sha1
_logger = logging.getLogger(__name__)
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    password = fields.Char('Contraseña')
    rol_type = fields.Selection([
        ('VERE', 'Vendedor'),
        ('VE', 'Preventa'),
        ('RE', 'Reparto')
    ], string='Type', copy=False, default='VERE')
    @api.model
    def create(self, vals):
        if vals['password'] is not False or vals['password'] is not  None:
            val=str(vals['password']).encode('utf-8')
            pasw= sha1(val).hexdigest()
            vals['password']=pasw
        return super(HrEmployee, self).create(vals)

    @api.one
    def write(self, vals):
        if vals.get('password'):
            val=str(vals['password']).encode('utf-8')
            pasw= sha1(val).hexdigest()
            vals['password']=pasw
        return super(HrEmployee, self).write(vals)


    def init(self):
            self._cr.execute("""

            CREATE OR REPLACE VIEW public.lx_employee
    AS SELECT hr_employee.id,
        hr_employee.name,
        hr_employee.active,
        hr_employee.address_home_id,
        hr_employee.country_id,
        hr_employee.gender,
        hr_employee.marital,
        hr_employee.birthday,
        hr_employee.ssnid,
        hr_employee.sinid,
        hr_employee.identification_id,
        hr_employee.passport_id,
        hr_employee.bank_account_id,
        hr_employee.permit_no,
        hr_employee.visa_no,
        hr_employee.visa_expire,
        hr_employee.address_id,
        hr_employee.work_phone,
        hr_employee.mobile_phone,
        COALESCE(hr_employee.work_email, 'pendiente@lataf.com'::character varying) AS work_email,
        hr_employee.work_location,
        hr_employee.job_id,
        hr_employee.department_id,
        hr_employee.parent_id,
        hr_employee.coach_id,
        hr_employee.notes,
        hr_employee.color,
        hr_employee.resource_id,
        hr_employee.company_id,
        hr_employee.create_uid,
        hr_employee.create_date,
        hr_employee.write_uid,
        hr_employee.write_date,
        hr_employee.password,
        3 AS id_supervisor,
            CASE
                WHEN ro.type::text = 'ENTREGA'::text THEN 'RE'::text
                ELSE 'VE'::text
            END AS clave_usuario_rol
       FROM hr_employee
         LEFT JOIN route_order ro ON ro.manage_id = hr_employee.id
      WHERE (hr_employee.id IN ( SELECT route_order.manage_id
               FROM route_order
              WHERE route_order.state::text = '0'::text));

CREATE OR REPLACE VIEW public.lx_price
AS SELECT p.id,
    p.default_code,
    p.active,
    p.product_tmpl_id,
    COALESCE(p.barcode, ''::character varying) AS barcode,
    p.volume,
    p.weight,
    p.create_uid,
    p.create_date,
    p.write_uid,
    p.write_date,
    pt.id AS pptemplate_id,
    pt.name,
    pt.sequence,
    COALESCE(pt.description, ''::text) AS description,
    pp.id AS pricelistitemid,
    pp.min_quantity,
    pp.applied_on,
    pp.base,
    pp.base_pricelist_id,
    pp.pricelist_id,
    pp.price_surcharge,
    pp.price_discount,
    pp.price_round,
    pp.price_min_margin,
    pp.price_max_margin,
    pp.currency_id,
    pp.date_start,
    pp.date_end,
    pp.compute_price,
    pp.fixed_price,
    pp.percent_price,
    pl.id AS pricelistid,
    pl.name AS pricelist,
    pl.active AS activepricelist,
    pl.discount_policy--,
 --   pl.website_id,
 --   pl.code,
 --   pl.selectable
   FROM product_product p
     LEFT JOIN product_template pt ON pt.id = p.product_tmpl_id
     LEFT JOIN product_pricelist_item pp ON pp.product_tmpl_id = pt.id
     LEFT JOIN product_pricelist pl ON pp.pricelist_id = pl.id
 -- WHERE pl.id = 3
    ;
 
    CREATE OR REPLACE VIEW public.lx_price_list
AS SELECT pp.id,
    pp.pricelist_id,
    p.id AS product_id,
    pp.fixed_price,
    pt.name,
    pp.create_uid,
    pp.write_uid,
    COALESCE(pp.create_date::timestamp with time zone, now()) AS create_date,
    COALESCE(pp.write_date::timestamp with time zone, now()) AS write_date
   FROM product_pricelist_item pp
     LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
    LEFT JOIN product_product p ON pt.id = p.product_tmpl_id
  WHERE pp.applied_on::text = '1_product'::text; 
  
CREATE OR REPLACE VIEW public.lx_res_partner
AS SELECT res_partner.id,
    res_partner.name,
    res_partner.company_id,
    res_partner.display_name,
    res_partner.date,
    res_partner.title,
    res_partner.parent_id,
    COALESCE(res_partner.ref, "left"(res_partner.name::text, 10)::character varying) AS ref,
    res_partner.lang,
    res_partner.tz,
    res_partner.user_id,
    res_partner.vat,
    res_partner.comment,
    res_partner.phone,
    res_partner.mobile,
    COALESCE(res_partner.city, ' '::character varying) AS city,
    res_partner.street,
    "left"(res_partner.street2::text, 49)::character varying AS street2,
    res_partner.zip,
    res_partner.write_uid,
    res_partner.write_date,
    COALESCE(res_partner.partner_latitude, 0::numeric) AS partner_latitude,
    COALESCE(res_partner.partner_longitude, 0::numeric) AS partner_longitude,
    COALESCE(( SELECT split_part(ir_property.value_reference::text, ','::text, 2)::integer AS split_part
           FROM ir_property
          WHERE ir_property.name::text = 'property_product_pricelist'::text AND ir_property.res_id::text = ('res.partner,'::text || res_partner.id)
         LIMIT 1),1) AS pricelist
   FROM res_partner
  WHERE (res_partner.id IN ( SELECT route_order.partner_id
           FROM route_order
          WHERE route_order.state::text = '0'::text));

            """)
