# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools ,_
from odoo.exceptions import except_orm, ValidationError,UserError
from odoo.exceptions import  AccessError, UserError, RedirectWarning,Warning
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta , date
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.exceptions
import re 
from odoo.http import request
from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
from ast import literal_eval
from odoo.addons.web.controllers.main import clean_action

class CRMLEAD(models.Model):
    _inherit = "crm.lead"

    quotation_template = fields.Many2one('sale.order.template',string='Quotation Template',track_visibility='onchange')



   
    