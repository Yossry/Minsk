# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime , timedelta , date
import calendar
from pytz import timezone
import pytz
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)
from collections import OrderedDict
import re

class crm_dashboard(models.TransientModel):
    _name = 'crm.dashboard'


    @api.model
    def get_dashboard_data(self):
        return {
            'total_customers' : self.env['res.partner'].search_count([('customer','=',True),('parent_id', '=', False)]),
            'total_leads':self.env['crm.lead'].search_count([('type','=','lead')]),
            'total_opportunities':self.env['crm.lead'].search_count([('type','=','opportunity')]),
            'total_expected_revenu':sum(lead.planned_revenue for lead in self.env['crm.lead'].search([])),
            'campaigns_by_roi':self.get_model_by_roi('utm.campaign','campaign_id'),
            'lead_per_campaign':self.get_lead_per_model('utm.campaign','campaign_id'),
            'lead_per_stage':self.get_lead_per_stage(),
            'converted_lead':self.get_converted_lead(),
            'conversion_rate':self.get_conversion_rate(),
            'log':self.get_log(),
            'user_activity_timeline':self.get_user_activity_timeline(),
        }
    
    @api.model
    def get_model_by_roi(self,model_name,field_name):
        
        models = []
        roi_val = []
        roi_percent = []
        models_objs = self.env[model_name].search_read([],['id','name'])
        for model in models_objs:
            models.append(model['name'])
            sales = self.env['sale.order'].search_read(
                [
                ('state','in',('sale','done')),
                (field_name,'=',model['id']),
                ('date_order', '>=', (datetime(datetime.today().year, 1, 1,0,0,0)).strftime('%Y-%m-%d 00:00:00')),
                ('date_order', '<=', (datetime(datetime.today().year, 12, 31,23,59,59)).strftime('%Y-%m-%d 00:00:00'))
                ]
                ,['amount_total'])
            sales_val = sum(i['amount_total'] for i in sales)
            costs = self.env['sales.markting.cost'].search_read(
                [
                ('state','=','done'),
                (field_name,'=',model['id']),
                ('date_of_investment', '>=', (datetime(datetime.today().year, 1, 1,0,0,0)).strftime('%Y-%m-%d 00:00:00')),
                ('date_of_investment', '<=', (datetime(datetime.today().year, 12, 31,23,59,59)).strftime('%Y-%m-%d 00:00:00'))
                ]
                ,['cost_of_investment'])
            costs_val = sum(i['cost_of_investment'] for i in costs)
            roi_val.append(sales_val - costs_val)
            if sales_val > 0 :
                roi_percent.append((sales_val - costs_val) / sales_val * 100)
            else:
                roi_percent.append(0)
        
        return {
            'models':models,
            'roi_val':roi_val,
            'roi_percent':roi_percent
        }
    
    @api.model
    def get_lead_per_model(self,model_name,field_name):
        sql = """
        SELECT
        coalesce(""" + model_name.replace(".","_") + """.id,0) as modl,
        count(crm_lead.id) lead_count,
        to_char(crm_lead.create_date, 'Mon') as month
        FROM crm_lead 
        LEFT JOIN """ + model_name.replace(".","_") + """ on crm_lead.campaign_id = """ + model_name.replace(".","_") + """.id
        WHERE date_part('year', crm_lead.create_date) = date_part('year', CURRENT_DATE)
        and crm_lead.active = true
        GROUP BY """ + model_name.replace(".","_") + """.id,
        to_char(crm_lead.create_date,'Mon') ,
        EXTRACT(MONTH FROM crm_lead.create_date)
        oRDER BY EXTRACT(MONTH FROM crm_lead.create_date)
        """
        self.env.cr.execute(sql)
        result  =  self.env.cr.dictfetchall()
        
        model_objs = self.env[model_name].search_read([],['id','name'])
        model_objs.append({'id': 0, 'name': u'undefined'})
        start_dates = str(datetime.today().year) + "-01-01"
        if datetime.today().month <= 11:
            end_dates = str(datetime.today().year) + "-" + str(datetime.today().month + 1) + "-01"
        else:
            end_dates = str(datetime.today().year + 1) + "-01-01"
        dates = [start_dates,end_dates]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = OrderedDict(((start + timedelta(_)).strftime(r"%b"), None) for _ in range((end - start).days)).keys()
        data = []
        for modl in model_objs:
            lead_count = []
            for month in months:
                no_data = True
                for row in result:
                    if row['month'] == month and modl['id'] == row['modl']:
                        lead_count.append(row['lead_count'])
                        no_data = False
                if no_data:
                    lead_count.append(0)
            data.append({'name':modl['name'],'data':lead_count})
        
        res = {
            'months':months,
            'series':data
        }
        return res
    
    
    @api.model
    def get_lead_per_stage(self):
        sql = """
        SELECT
        coalesce(crm_stage.id,0) as utm_campaign,
        count(crm_lead.id) lead_count,
        to_char(crm_lead.create_date, 'Mon') as month
        FROM crm_lead 
        LEFT JOIN crm_stage on crm_lead.stage_id = crm_stage.id
        WHERE date_part('year', crm_lead.create_date) = date_part('year', CURRENT_DATE)
        and active = true
        GROUP BY crm_stage.id,
        to_char(crm_lead.create_date,'Mon') ,
        EXTRACT(MONTH FROM crm_lead.create_date)
        oRDER BY EXTRACT(MONTH FROM crm_lead.create_date)
        """
        self.env.cr.execute(sql)
        result  =  self.env.cr.dictfetchall()
        
        stage_objs = self.env['crm.stage'].search_read([],['id','name'])
        stage_objs.append({'id': 0, 'name': u'undefined'})

        start_dates = str(datetime.today().year) + "-01-01"
        if datetime.today().month <= 11:
            end_dates = str(datetime.today().year) + "-" + str(datetime.today().month + 1) + "-01"
        else:
            end_dates = str(datetime.today().year + 1) + "-01-01"
        dates = [start_dates,end_dates]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = OrderedDict(((start + timedelta(_)).strftime(r"%b"), None) for _ in range((end - start).days)).keys()
        data = []
        for stage in stage_objs:
            lead_count = []
            for month in months:
                no_data = True
                for row in result:
                    if row['month'] == month and stage['id'] == row['utm_campaign']:
                        lead_count.append(row['lead_count'])
                        no_data = False
                if no_data:
                    lead_count.append(0)
            data.append({'name':stage['name'],'data':lead_count})
        
        res = {
            'months':months,
            'series':data
        }
        return res
    
    @api.model
    def get_converted_lead(self):
        sql = """SELECT
        count(crm_lead.id) lead_count,
        to_char(crm_lead.date_conversion, 'Mon') as month
        FROM crm_lead 
        WHERE date_part('year', crm_lead.date_conversion) = date_part('year', CURRENT_DATE)
        and active = true
        GROUP BY
        to_char(crm_lead.date_conversion,'Mon') ,
        EXTRACT(MONTH FROM crm_lead.date_conversion)
        oRDER BY EXTRACT(MONTH FROM crm_lead.date_conversion)"""
        self.env.cr.execute(sql)
        result  =  self.env.cr.dictfetchall()

        start_dates = str(datetime.today().year) + "-01-01"
        if datetime.today().month <= 11:
            end_dates = str(datetime.today().year) + "-" + str(datetime.today().month + 1) + "-01"
        else:
            end_dates = str(datetime.today().year + 1) + "-01-01"
        dates = [start_dates,end_dates]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = OrderedDict(((start + timedelta(_)).strftime(r"%b"), None) for _ in range((end - start).days)).keys()
        data = []
        lead_count = []
        for month in months:
            no_data = True
            for row in result:
                if row['month'] == month:
                    lead_count.append(row['lead_count'])
                    no_data = False
            if no_data:
                lead_count.append(0)
        data.append({'name':'Converted Date','data':lead_count})
        
        res = {
            'months':months,
            'series':data
        }
        return res
    
    
    @api.model
    def get_conversion_rate(self):
        sql = """
        SELECT
        count(crm_lead.id) lead_count,
        sales_count,
        to_char(crm_lead.create_date, 'Mon') as month
        FROM crm_lead

        left join (
        SELECT
        count(sale_order.id) sales_count,
        to_char(sale_order.create_date, 'Mon') as month
        FROM sale_order 
        WHERE date_part('year', sale_order.create_date) = date_part('year', CURRENT_DATE)
        and state != 'cancel'
        GROUP BY
        to_char(sale_order.create_date,'Mon') ,
        EXTRACT(MONTH FROM sale_order.create_date)
        oRDER BY EXTRACT(MONTH FROM sale_order.create_date)
        ) sales_data on sales_data.month = to_char(crm_lead.create_date, 'Mon')
        
        WHERE date_part('year', crm_lead.create_date) = date_part('year', CURRENT_DATE)
        and active = true
        GROUP BY
        to_char(crm_lead.create_date,'Mon') ,sales_count,
        EXTRACT(MONTH FROM crm_lead.create_date)
        oRDER BY EXTRACT(MONTH FROM crm_lead.create_date)
        """
        self.env.cr.execute(sql)
        result  =  self.env.cr.dictfetchall()

        start_dates = str(datetime.today().year) + "-01-01"
        if datetime.today().month <= 11:
            end_dates = str(datetime.today().year) + "-" + str(datetime.today().month + 1) + "-01"
        else:
            end_dates = str(datetime.today().year + 1) + "-01-01"
        dates = [start_dates,end_dates]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months = OrderedDict(((start + timedelta(_)).strftime(r"%b"), None) for _ in range((end - start).days)).keys()
        data = []
        lead_count = []
        for month in months:
            no_data = True
            for row in result:
                if row['month'] == month:
                    sales_number = float(row['sales_count']) if row['sales_count'] is not None else 0
                    lead_number = float(row['lead_count']) if row['lead_count'] is not None else 0
                    conversion_rate = 0
                    if lead_number > 0:
                        conversion_rate = sales_number / lead_number * 100
                    lead_count.append(conversion_rate)
                    no_data = False
            if no_data:
                lead_count.append(0)
        data.append({'name':'Conversion Rate','data':lead_count})
        
        res = {
            'months':months,
            'series':data
        }
        return res
        #Conversion Rate = Total Number of Sales / Number of Unique Visitors * 100
    
    
    @api.model
    def get_log(self):
        messages = self.env['mail.message'].search_read([('model','=','crm.lead'),('body','!=','')],['res_id','model','body','date'],limit = 5,order="id desc")
        data = []
        for message in messages:
            now_utc = datetime.utcnow()
            record_date_utc = message['date']
            d = now_utc - record_date_utc
            hours = int(d.seconds / 3600)
            if d.days == 0 and hours < 1 :
                date = 'from ' + str(d.seconds/60) + ' minutes ago'
            elif d.days == 0 and hours < 24 :
                date = 'from ' + str(hours) + ' hours ago'
            else:
                date = 'from ' + str(d.days) + ' days ago'
            
            log_data = self.env[message['model']].browse(message['res_id'])
            log_data_str = log_data.partner_id.name + u' | ' if log_data.partner_id else ''
            log_data_str = log_data_str + log_data.name if log_data else ''
            data.append({
                'body': re.sub(r'<[^>]*?>', '', message['body']),
                'date': str(date),
                'log_data': log_data_str,
            })
        return data
    
    
    @api.model
    def get_user_activity_timeline(self):
        messages = self.env['mail.message'].search_read([('body','!=',''),('model','=','crm.lead')],['res_id','model','create_uid','body','date'],limit = 5,order="id desc")
        data = []
        for message in messages:
            now_utc = datetime.utcnow()
            record_date_utc = message['date']
            d = now_utc - record_date_utc
            hours = int(d.seconds / 3600)
            if d.days == 0 and hours < 1 :
                date = 'from ' + str(d.seconds/60) + ' minutes ago'
            elif d.days == 0 and hours < 24 :
                date = 'from ' + str(hours) + ' hours ago'
            else:
                date = 'from ' + str(d.days) + ' days ago'
            
            user = self.env['res.users'].browse(message['create_uid'][0])
            
            data.append({
                'user_name':user.name,
                'user_image':'/web/image?model=res.users&field=image_small&id=' + str(user.id),
                'body': re.sub(r'<[^>]*?>', '', message['body']),
                'date': str(date),
                'log_data': self.env[message['model']].browse(message['res_id']).name,
            })
        return data
    