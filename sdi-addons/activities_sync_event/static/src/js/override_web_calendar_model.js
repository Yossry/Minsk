odoo.define('sdi_crm_calendar', function (require){
"use strict";
// require 1original module JS
var CalendarModel = require('web.CalendarModel');
var sdi_calendar = CalendarModel.include({
    /**
     *
     * @override
     * @param {any} params
     * @returns {Deferred}
     */
    load: function (params)
    {

        var self = this;
        this.modelName = params.modelName;

        if (params.modelName === 'calendar.event')
        {
            params.fieldNames.push('editable');
        }
        this.fields = params.fields;
        this.fieldNames = params.fieldNames;
        this.fieldsInfo = params.fieldsInfo;
        this.mapping = params.mapping;
        this.mode = params.mode;       // one of month, week or day
        this.scales = params.scales;   // one of month, week or day

        // Check whether the date field is editable (i.e. if the events can be
        // dragged and dropped)
        this.editable = params.editable;
        this.creatable = params.creatable;

        // display more button when there are too much event on one day
        this.eventLimit = params.eventLimit;

        // fields to display color, e.g.: user_id.partner_id
        this.fieldColor = params.fieldColor;
        if (!this.preload_def)
        {
            this.preload_def = $.Deferred();
            $.when(
                this._rpc({model: this.modelName, method: 'check_access_rights', args: ["write", false]}),
                this._rpc({model: this.modelName, method: 'check_access_rights', args: ["create", false]}))
            .then(function (write, create) {
                self.write_right = write;
                self.create_right = create;
                self.preload_def.resolve();
            });
        }

        this.data =
        {
            domain: params.domain,
            context: params.context,
            // get in arch the filter to display in the sidebar and the field to read
            filters: params.filters,
        };

        // Use mode attribute in xml file to specify zoom timeline (day,week,month)
        // by default month.
        this.setDate(params.initialDate, true);
        this.setScale(params.mode);

        _.each(this.data.filters, function (filter)
        {
            if (filter.avatar_field && !filter.avatar_model)
            {
                filter.avatar_model = self.modelName;
            }
        });

        return this.preload_def.then(this._loadCalendar.bind(this));
    },
    /**
     * Modificado para que el evento sea o no editable en función de si la
     * actividad a la que puede estar relacionado se haya marcado como hecha.
     * @override
     * Transform OpenERP event object to fullcalendar event object
     */
    _recordToCalendarEvent: function (evt)
    {
        var date_start;
        var date_stop;
        var date_delay = evt[this.mapping.date_delay] || 1.0,
            all_day = this.mapping.all_day ? evt[this.mapping.all_day] : false,
            the_title = '',
            attendees = [];

        if (!all_day) {
            date_start = evt[this.mapping.date_start].clone();
            date_stop = this.mapping.date_stop ? evt[this.mapping.date_stop].clone() : null;
        } else {
            date_start = evt[this.mapping.date_start].clone().startOf('day');
            date_stop = this.mapping.date_stop ? evt[this.mapping.date_stop].clone().startOf('day') : null;
        }

        if (!date_stop && date_delay) {
            date_stop = date_start.clone().add(date_delay,'hours');
        }

        if (!all_day) {
            date_start.add(this.getSession().getTZOffset(date_start), 'minutes');
            date_stop.add(this.getSession().getTZOffset(date_stop), 'minutes');
        }

        if (this.mapping.all_day && evt[this.mapping.all_day]) {
            date_stop.add(1, 'days');
        }
        var isAllDay = this.fields[this.mapping.date_start].type === 'date' ||
                        this.mapping.all_day && evt[this.mapping.all_day] || false;

        var r = {
            'record': evt,
            'start': date_start,
            'end': date_stop,
            'r_start': date_start,
            'r_end': date_stop,
            'title': the_title,
            'allDay': isAllDay,
            'id': evt.id,
            'attendees':attendees,
            'editable':evt.editable,
        };

        if (this.mapping.all_day && evt[this.mapping.all_day]) {
            // r.start = date_start.format('YYYY-MM-DD');
            // r.end = date_stop.format('YYYY-MM-DD');
        } else if (this.data.scale === 'month' && this.fields[this.mapping.date_start].type !== 'date') {
            // In month, FullCalendar gives the end day as the
            // next day at midnight (instead of 23h59).
            date_stop.add(1, 'days');

            // allow to resize in month mode
            r.reset_allday = r.allDay;
            r.allDay = true;
            r.start = date_start.format('YYYY-MM-DD');
            r.end = date_stop.startOf('day').format('YYYY-MM-DD');
        }

        return r;
    },

})
return sdi_calendar;
});
