# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
from datetime import datetime, timedelta
import pytz
import copy
import logging

_logger = logging.getLogger(__name__)

# TODO: decide if we are dependent on this variable or the imported schedule duration.
# LOCAL_TZ: Local timezone 
LOCAL_TZ = 'Europe/Stockholm'
# BASE_DURATION: Base duration given by TeleOpti. This is the duration of the calendar.schedule slots in minutes.
BASE_DURATION = 30.0
# BASE_DAY_START, BASE_DAY_STOP: The hours between which we normally accept appointments
BASE_DAY_START = pytz.timezone(LOCAL_TZ).localize(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)).astimezone(pytz.utc)
BASE_DAY_STOP = pytz.timezone(LOCAL_TZ).localize(datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)).astimezone(pytz.utc)
# RESERVED_TIMEOUT is the default time before a reservation times out.
RESERVED_TIMEOUT = 300.0

# Termer
# occasions = bokningsbara tider
# schemaläggning = resursplanering?

class CalendarSchedule(models.Model):
    _name = 'calendar.schedule'
    _description = "Schedule"

    name = fields.Char(string='Name', required=True)
    start = fields.Datetime(string='Start', required=True, help="Start date of a schedule")
    stop = fields.Datetime(string='Stop', required=True, help="Stop date of a schedule")
    duration = fields.Float('Duration')
    scheduled_agents = fields.Integer(string='Scheduled agents', help="Number of scheduled agents")
    forecasted_agents = fields.Integer(string='Forecasted agents', help="Number of forecasted agents")
    type_id = fields.Many2one(string='Meeting type', comodel_name='calendar.appointment.type', help="Related meeting type")
    channel = fields.Many2one(string='Channel', comodel_name='calendar.channel')

    @api.multi
    def create_occasions(self):
        """Creates a number of occasions from schedules, depending on number of scheduled agents"""
        for schedule in self:
            no_occasions = self.env['calendar.occasion'].search_count([('start', '=', schedule.start), ('type_id', '=', schedule.type_id.id), ('additional_booking', '=', False)])
            if (schedule.scheduled_agents - no_occasions) > 0:
                vals = {
                    'name': '%sm @ %s' % (schedule.duration, schedule.start.strftime("%Y-%m-%dT%H:%M:%S")),
                    'duration': schedule.duration,
                    'start': schedule.start,
                    'stop': schedule.stop,
                    'type_id': schedule.type_id.id,
                    'channel': schedule.channel,
                    'additional_booking': False,
                    'state': 'ok',
                }
                for occasion in range(schedule.scheduled_agents - no_occasions):
                    self.env['calendar.occasion'].create(vals)

            elif (schedule.scheduled_agents - no_occasions) < 0:
                # TODO: handle this case better
                pass

class CalendarAppointmentType(models.Model):
    _name = 'calendar.appointment.type'
    _description = "Meeting type"

    name = fields.Char('Name', required=True)
    ipf_id = fields.Char('IPF Id', required=True, help="The IPF type id, if this is wrong the integration won't work")
    # mötestyps_id
    channel = fields.Many2one(string='Channel', comodel_name='calendar.channel')
    ipf_num = fields.Integer(string='IPF Number')
    additional_booking = fields.Boolean(string='Over booking')
    # ärendetyp ace
    # könamn ace
    # standardtid, möte.
    # add competence

class CalendarChannel(models.Model):
    _name = 'calendar.channel'
    _description = "Channel"

    name = fields.Char('Name', required=True)

class CalendarMappedDates(models.Model):
    _name = 'calendar.mapped_dates'
    _description = "Mapped dates"

    name = fields.Char(string="Name")
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

class CalendarAppointment(models.Model):
    _name = 'calendar.appointment'
    _description = "Appointment"

    name = fields.Char(string='Name', required=True)
    start = fields.Datetime(string='Start', required=True, help="Start date of an appointment")
    stop = fields.Datetime(string='Stop', required=True, help="Stop date of an appointment")
    duration = fields.Float('Duration')
    user_id = fields.Many2one(string='Case worker', comodel_name='res.users', help="Booked case worker")
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner', help="Booked customer")
    state = fields.Selection(selection=[('free', 'Free'),
                                        ('reserved', 'Reserved'),
                                        ('confirmed', 'Confirmed')],
                                        string='State', 
                                        default='free', 
                                        help="Status of the meeting")
    location_code = fields.Char(string='Location')
    office = fields.Many2one('res.partner', string="Office")
    office_code = fields.Char(string='Office code', related="office.office_code")
    occasion_ids = fields.One2many(comodel_name='calendar.occasion', inverse_name='appointment_id', string="Occasion")
    # type_id = fields.Many2one(string='Type', related='occasion_ids.type_id')
    type_id = fields.Many2one(string='Type', required=True, comodel_name='calendar.appointment.type')
    # channel =  fields.Char(string='Channel', related='occasion_ids.channel')
    channel =  fields.Many2one(string='Channel', required=True, comodel_name='calendar.channel', related='type_id.channel')
    additional_booking = fields.Boolean(String='Over booking', related='occasion_ids.additional_booking')
    reserved = fields.Datetime(string='Reserved', help="Occasions was reserved at this date and time")

    def confirm_appointment(self):
        """Confirm reserved booking"""
        if self.state == 'reserved':
            self.state = 'confirmed'
            res = True
        else: 
            res = False

        return res

    # TODO: consider using _force_create_occasion instead (/in addition?) in create and update?

    @api.model
    def create(self, values):
        res = False
        start = datetime.strptime(values.get('start'), "%Y-%m-%d %H:%M:%S")
        stop = datetime.strptime(values.get('stop'), "%Y-%m-%d %H:%M:%S")
        duration = values.get('duration') * 60 # convert from hours to minutes
        type_id = self.env['calendar.appointment.type'].browse(values.get('type_id'))

        occasions = self.env['calendar.occasion'].get_bookable_occasions(start, stop, duration, type_id, values.get('channel'))
        if occasions:
            values['occasion_ids'] =  [(6,0, [occasion.id for occasion in occasions[0]])]
            # TODO: query user before moving appointment?
            values['start'] = occasions[0][0].start
            values['stop'] = occasions[0][len(occasions[0]) - 1].stop
            res = super(CalendarAppointment, self).create(values)
        return res

    @api.model
    def update(self, values):
        res = False
        start = datetime.strptime(values.get('start'), "%Y-%m-%d %H:%M:%S")
        stop = datetime.strptime(values.get('stop'), "%Y-%m-%d %H:%M:%S")
        duration = values.get('duration') * 60 # convert from hours to minutes
        type_id = self.env['calendar.appointment.type'].browse(values.get('type_id'))

        occasions = self.env['calendar.occasion'].get_bookable_occasions(start, stop, duration, type_id, values.get('channel'))
        if occasions:
            values['occasion_ids'] =  [(6,0, [occasion.id for occasion in occasions[0]])]
            # TODO: query user before moving appointment?
            values['start'] = occasions[0][0].start
            values['stop'] = occasions[0][len(occasions[0]) - 1].stop
            res = super(CalendarAppointment, self).write(values)
        return res

class CalendarOccasion(models.Model):
    _name = 'calendar.occasion'
    _description = "Occasion"

    name = fields.Char(string='Name', required=True)
    start = fields.Datetime(string='Start', required=True, help="Start date of an occasion")
    stop = fields.Datetime(string='Stop', required=True, help="Stop date of an occasion")
    duration = fields.Float('Duration')
    appointment_id = fields.Many2one(comodel_name='calendar.appointment', string="Appointment")
    type_id = fields.Many2one(comodel_name='calendar.appointment.type', string='Type')
    channel = fields.Many2one(string='Channel', comodel_name='calendar.channel', related='type_id.channel')
    additional_booking = fields.Boolean(String='Over booking')
    user_id = fields.Many2one(string='Case worker', comodel_name='res.users', help="Booked case worker")
    state = fields.Selection(selection=[('request', 'Awaiting acceptance'),
                                        ('ok', 'Ready to book'),
                                        ('fail', 'Denied')],
                                        string='Occasion state', 
                                        default='request', 
                                        help="Status of the meeting")

    @api.model
    def _force_create_occasion(self, duration, start, type_id, channel, state):
        """In case we need to force through a new occasion for some reason"""
        vals = {
            'name': '%sm @ %s' % (duration, start),
            'start': start,
            'stop': start + timedelta(minutes=duration),
            'duration': duration,
            'appointment_id': False,
            'type_id': type_id,
            'channel': channel,
            'additional_booking': True,
            'state': state,
        }
        res = self.env['calendar.occasion'].create(vals)
        return res

    @api.model
    def _get_min_occasions(self, type_id, date_start=None, date_stop=None):
        """Returns the timeslot (as a start date, DateTime) with the least 
        amount of occurances for a specific timeframe"""
        date_start = date_start or copy.copy(BASE_DAY_START)
        date_stop= date_stop or copy.copy(BASE_DAY_STOP)
        go = True
        loop_date = date_start
        occ_time = {}
        while go:
            occ_time[loop_date.strftime("%Y-%m-%dT%H:%M:%S")] = self.env['calendar.occasion'].search_count([('start', '=', loop_date),('type_id', '=', type_id.id)])
            loop_date = loop_date + timedelta(minutes=BASE_DURATION)
            if loop_date >= date_stop:
                go = False
        occ_time_min_key = min(occ_time, key=occ_time.get)
        res = datetime.strptime(occ_time_min_key, "%Y-%m-%dT%H:%M:%S")
        return res

    @api.model
    def _check_date_mapping(self, date):
        """Checks if a date has a mapped date, and returns the mapped date 
        if it exists """
        mapped_date = self.env['calendar.mapped_dates'].search([('from_date', '=', date)])
        if mapped_date:
            res = mapped_date.to_date 
        else:
            res = date
        return res

    @api.model
    def _get_additional_booking(self, date, duration, type_id, channel):
        """"Creates extra, additional, occasions"""
        # Replace date with mapped date if we have one
        date = self._check_date_mapping(date)
        date_list = date.strftime("%Y-%-m-%-d").split("-")
        # Copy to make sure we dont overwrite BASE_DAY_START or BASE_DAY_STOP
        day_start = copy.copy(BASE_DAY_START)
        day_stop = copy.copy(BASE_DAY_STOP)
        # Ugly, ugly code..
        day_start.replace(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]))
        day_stop.replace(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]))
        # Find when to create new occasion
        start_date = self._get_min_occasions(type_id, day_start, day_stop)
        # Calculate how many occasions we need
        no_occasions = int(duration / BASE_DURATION)
        # Create new occasions.
        res = self.env['calendar.occasion']
        for i in range(no_occasions):
            vals = {
                'name': '%sm @ %s' % (duration, start_date),
                'start': start_date,
                'stop': start_date + timedelta(minutes=BASE_DURATION),
                'duration': BASE_DURATION,
                'appointment_id': False,
                'type_id': type_id.id,
                'channel': channel,
                'additional_booking': True,
                'state': 'ok',
            }
            res |= self.env['calendar.occasion'].create(vals)
            start_date = start_date + timedelta(minutes=BASE_DURATION)
        return res

    @api.multi
    def approve_occasion(self):
        """Approve suggested occasion"""
        if self.state == 'request':
            self.state = 'ok'
            ret = True
        else:
            ret = False

        return ret

    @api.multi
    def deny_occasion(self):
        """Deny suggested occasion"""
        if self.state == 'request':
            self.state = 'fail'
            ret = True
        else:
            ret = False

        return ret

    @api.model
    def get_bookable_occasions(self, start, stop, duration, type_id, channel, max_depth = 1):
        """Returns a list of occasions matching the defined parameters of the appointment. Creates additional 
        occasions if allowed."""
        # Calculate number of occasions needed to match booking duration
        no_occasions = int(duration / BASE_DURATION)
        date_delta = (stop - start)

        occ_lists = []
        # declare lists...
        for i in range(max_depth):
            occ_lists.append([])

        # find occasions for each day, starting with last day
        for day in range(date_delta.days or 1):
            # find 'no_occasions' number of free occasions for each timeslot
            for i in range(no_occasions):
                iteration_start = start + timedelta(minutes=BASE_DURATION) * i
                occasion_ids = self.env['calendar.occasion'].search([('start', '=', iteration_start + timedelta(days=(date_delta.days - day))), ('type_id', '=', type_id.id), ('channel', '=', channel), ('appointment_id', '=', False)], limit=max_depth)
                # save one result from each timeslot in a seperate list 
                for j in range(len(occasion_ids)):
                    occ_lists[j] += occasion_ids[j]

        # if type allows additional bookings and  we didn't find any
        # free occasions, create new ones:
        for day in range(date_delta.days or 1):
            if len(occ_lists[day]) != no_occasions:
                if type_id.additional_booking:
                    day_start = start + timedelta(days=(date_delta.days - day))
                    occ_lists[day] = self._get_additional_booking(day_start, duration, type_id, channel)
                # TODO: else: remove partial matches, these are unusable
                # del occ_lists[i]
                # del will cause problems with the for loop..

        res = occ_lists

        return res

    @api.model
    def reserve_occasion(self, occasion_ids):
        """Reserves an occasion."""
        start = occasion_ids[0].start
        stop = occasion_ids[len(occasion_ids)-1].stop
        duration = stop.minute - start.minute 

        # check that occasions are free and unreserved
        free = True
        for occasion_id in occasion_ids:
            if (occasion_id.appointment_id and occasion_id.appointment_id.state != 'reserved') or (occasion_id.appointment_id and occasion_id.appointment_id.state == 'reserved' and occasion_id.reserved > datetime.now() - timedelta(seconds=RESERVED_TIMEOUT)):
                free = False

        if free:
            vals = {
                'name': occasion_ids[0].type_id.name,
                'start': start,
                'stop': stop,
                'duration': duration,
                'user_id': False,
                'partner_id': False,
                'state': 'reserved',
                'location_code': False,
                'office': False,
                'occasion_ids': occasion_ids, # I dont think this does anything?
                'reserved': datetime.now(),
            }
            appointment = self.env['calendar.appointment'].create(vals)

            # relation needs to be set from calendar.occasion 
            for occasion_id in occasion_ids:
                occasion_id.appointment_id = appointment.id

            res = appointment
        else:
            # TODO: implement error codes..
            res = '200' # 400, 403, 404, 500

        return res
