# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################

from odoo import models, fields, api
from odoo.http import request
import datetime

class FreightDashboard(models.Model):
    _name = 'freight.dashboard'
    _description = 'Freight Dashboard'

    name = fields.Char("")

    @api.model
    def get_employee_info(self):
        uid = request.session.uid
        cr = self.env.cr
        employee_id = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        operation_search_view_id = self.env.ref('freight.view_freight_operation_filter')
        invoice_search_view_id = self.env.ref('account.view_account_invoice_filter')
        freight_port_search_id = self.env.ref('freight.view_freight_port_filter')
        direct_operation_count = self.env['freight.operation'].sudo().search_count([('operation', '=', 'direct')])
        house_operation_count = self.env['freight.operation'].sudo().search_count([('operation', '=', 'house')])
        master_operation_count = self.env['freight.operation'].sudo().search_count([('operation', '=', 'master')])
        port_count = self.env['freight.port'].sudo().search_count([('active', '=', True)])
        invoice_count = self.env['account.invoice'].sudo().search_count([('type', '=', 'out_invoice')])
        bills_count = self.env['account.invoice'].sudo().search_count([('type', '=', 'in_invoice')])

        # payroll Datas for Bar chart
        operation_labels = []
        operation_dataset = []
        if direct_operation_count:
            operation_labels.append('Direct')
            operation_dataset.append(direct_operation_count)
        if house_operation_count:
            operation_labels.append('House')
            operation_dataset.append(house_operation_count)
        if master_operation_count:
            operation_labels.append('Master')
            operation_dataset.append(master_operation_count)

        shippers = self.env['res.partner'].sudo().search([('active', '=', 'True')])
        shipper_labels = []
        shipper_dataset = []
        if shippers:
            for line in shippers:
                shipper_count = self.env['freight.operation'].sudo().search_count([('shipper_id', '=', line.id)])
                if shipper_count:
                    shipper_labels.append(line.name)
                    shipper_dataset.append(shipper_count)


        query = """
            select e.name as name, e.direction as direction, e.transport as transport, e.operation as operation,
            partner.name as shipper, port.name as source_location, port_two.name as destination_location
            from freight_operation e 
            left join res_partner partner on (partner.id = e.shipper_id)
            left join freight_port port on (e.source_location_id = port.id)
            left join freight_port port_two on (e.destination_location_id = port_two.id)
        """

        cr.execute(query)
        operation_table = cr.dictfetchall()

        if employee_id:
            categories = self.env['hr.employee.category'].sudo().search([('id', 'in', employee_id[0]['category_ids'])])
            data = {
                'categories': [c.name for c in categories],
                'operation_search_view_id': operation_search_view_id.id,
                'invoice_search_view_id': invoice_search_view_id.id,
                'freight_port_search_id':freight_port_search_id.id,
                'house_operation_count': house_operation_count,
                'master_operation_count': master_operation_count,
                'direct_operation_count': direct_operation_count,
                'operation_labels': operation_labels,
                'operation_dataset': operation_dataset,
                'shipper_labels': shipper_labels,
                'shipper_dataset': shipper_dataset,
                'operation_table': operation_table,
                'invoice_count':invoice_count,
                'bills_count':bills_count,
                'port_count':port_count,
            }
            employee_id[0].update(data)
        return employee_id