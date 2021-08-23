odoo.define('uppercrust_backend_theme.GraphRenderer', function (require) {
    "use strict";

    var GraphRenderer = require('web.GraphRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _t = core._t;
    var qweb = core.qweb;

    var CHART_TYPES = ['pie', 'bar', 'line'];

    // hide top legend when too many items for device size
    var MAX_LEGEND_LENGTH = 25 * (Math.max(1, config.device.size_class));

    return GraphRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            core.bus.on('toggle_graph_sidebar', this, this._onToggleSearchbar);
        },
        _onToggleSearchbar: function (is_visible) {
            this.getParent().reload();
        },
        start: function () {
            var self = this;
            this.theme_colors = [];
        },
        _fetchThemeColors: function () {
            var self = this;
            return self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['uppercrust_backend_theme.selected_theme']
            }).then(function (theme_id) {
                return self._rpc({
                    model: 'ir.web.theme',
                    method: 'search_read',
                    domain: [['id', '=', parseInt(theme_id)]],
                    fields: ['leftbar_color', 'buttons_color', 'tag_info',
                        'tag_danger', 'tag_success', 'tag_warning',
                        'tag_primary', 'tag_muted'],
                }).then(function (result) {
                    if (!_.isEmpty(result)) {
                        self.theme_colors.push(result[0].buttons_color, result[0].leftbar_color, result[0].tag_info, result[0].tag_danger,
                                result[0].tag_success, result[0].tag_warning, result[0].tag_primary, result[0].tag_muted)
                    }
                });
            });
        },
        _render: function () {
            var self = this;
            if (this.to_remove) {
                nv.utils.offWindowResize(this.to_remove);
            }
            if (!_.contains(CHART_TYPES, this.state.mode)) {
                this.$el.empty();
                this.trigger_up('warning', {
                    title: _t('Invalid mode for chart'),
                    message: _t('Cannot render chart with mode : ') + this.state.mode
                });
            } else if (!this.state.data.length) {
                this.$el.empty();
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("No data to display"),
                    description: _t("Try to add some records, or make sure that " +
                            "there is no active filter in the search bar."),
                }));
            } else if (this.isInDOM) {
                // only render the graph if the widget is already in the DOM (this
                // happens typically after an update), otherwise, it will be
                // rendered when the widget will be attached to the DOM (see
                // 'on_attach_callback')
                this._fetchThemeColors().then(function () {
                    self._renderGraph();
                });
            }
            return this._super.apply(this, arguments);
        },
        _processColors: function (n_elements) {
            return this.theme_colors;
        },
        _renderBarChart: function () {
            // prepare data for bar chart
            var self = this;
            var data = [];
            var values;
            var measure = this.state.fields[this.state.measure].string;

            // undefined label value becomes a string 'Undefined' translated
            this.state.data.forEach(self._sanitizeLabel);

            if (this.state.groupedBy.length === 0) {
                data = [{
                    values: [{
                        x: measure,
                        y: this.state.data[0].value
                    }],
                    key: measure
                }];
            } else if (this.state.groupedBy.length === 1) {
                values = this.state.data.map(function (datapt, index) {
                    if (self.state.comparisonData) {
                        return {x: index, y: datapt.value};
                    } else {
                        return {x: datapt.labels, y: datapt.value};
                    }
                });
                data.push({
                    values: values,
                    key: measure,
                });
                if (this.state.comparisonData) {
                    values = this.state.comparisonData.map(function (datapt, index) {
                        return {x: index, y: datapt.value};
                    });
                    data.push({
                        values: values,
                        key: measure + ' (compare)',
                        color: '#ff7f0e',
                    });
                }
            } else if (this.state.groupedBy.length > 1) {
                var xlabels = [],
                        series = [],
                        label, serie, value;
                values = {};
                for (var i = 0; i < this.state.data.length; i++) {
                    label = this.state.data[i].labels[0];
                    serie = this.state.data[i].labels[1];
                    value = this.state.data[i].value;
                    if ((!xlabels.length) || (xlabels[xlabels.length - 1] !== label)) {
                        xlabels.push(label);
                    }
                    series.push(this.state.data[i].labels[1]);
                    if (!(serie in values)) {
                        values[serie] = {};
                    }
                    values[serie][label] = this.state.data[i].value;
                }
                series = _.uniq(series);
                data = [];
                var current_serie, j;
                for (i = 0; i < series.length; i++) {
                    current_serie = {values: [], key: series[i]};
                    for (j = 0; j < xlabels.length; j++) {
                        current_serie.values.push({
                            x: xlabels[j],
                            y: values[series[i]][xlabels[j]] || 0,
                        });
                    }
                    data.push(current_serie);
                }
            }

            // For Bar chart View, we keep only groups where count > 0
            data[0].values = _.filter(data[0].values, function (elem, index) {
                return self.state.data[index].count > 0;
            });

            var $svgContainer = $('<div/>', {class: 'o_graph_svg_container'});
            this.$el.append($svgContainer);
            var svg = d3.select($svgContainer[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(0);
            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.multiBarChart();
            chart.options({
                margin: {left: 80, bottom: 100, top: 80, right: 0},
                delay: 100,
                transition: 10,
                showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                showXAxis: true,
                showYAxis: true,
                rightAlignYAxis: false,
                stacked: this.stacked,
                reduceXTicks: false,
                rotateLabels: -20,
                showControls: (this.state.groupedBy.length > 1),
                color: colors,
            });
            chart.yAxis.tickFormat(function (d) {
                var measure_field = self.state.fields[self.measure];
                return field_utils.format.float(d, {
                    digits: measure_field && measure_field.digits || [69, 2],
                });
            });

            chart(svg);
            return chart;
        },
        _renderPieChart: function (stateData) {
            var self = this;
            var data = [];
            var all_negative = true;
            var some_negative = false;
            var all_zero = true;

            // undefined label value becomes a string 'Undefined' translated
            stateData.forEach(self._sanitizeLabel);

            stateData.forEach(function (datapt) {
                all_negative = all_negative && (datapt.value < 0);
                some_negative = some_negative || (datapt.value < 0);
                all_zero = all_zero && (datapt.value === 0);
            });
            if (some_negative && !all_negative) {
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("Invalid data"),
                    description: _t("Pie chart cannot mix positive and negative numbers. " +
                            "Try to change your domain to only display positive results"),
                }));
                return;
            }
            if (all_zero) {
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("Invalid data"),
                    description: _t("Pie chart cannot display all zero numbers.. " +
                            "Try to change your domain to display positive results"),
                }));
                return;
            }
            if (this.state.groupedBy.length) {
                data = stateData.map(function (datapt) {
                    return {x: datapt.labels.join("/"), y: datapt.value};
                });
            }

            // We only keep groups where count > 0
            data = _.filter(data, function (elem, index) {
                return stateData[index].count > 0;
            });

            var $svgContainer = $('<div/>', {class: 'o_graph_svg_container'});
            this.$el.append($svgContainer);
            var svg = d3.select($svgContainer[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(100);

            var legend_right = config.device.size_class > config.device.SIZES.VSM;
            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.pieChart().labelType('percent');
            chart.options({
                delay: 250,
                showLegend: legend_right || _.size(data) <= MAX_LEGEND_LENGTH,
                legendPosition: legend_right ? 'right' : 'top',
                transition: 100,
                color: colors,
            });

            chart(svg);
            return chart;
        },
        _renderLineChart: function () {
            var self = this;

            // Remove Undefined of first GroupBy
            var graphData = _.filter(this.state.data, function (elem) {
                return elem.labels[0] !== undefined;
            });

            // undefined label value becomes a string 'Undefined' translated
            this.state.data.forEach(self._sanitizeLabel);

            var data = [];
            var tickValues;
            var tickFormat;
            var measure = this.state.fields[this.state.measure].string;
            var values;

            if (this.state.groupedBy.length === 1) {
                values = graphData.map(function (datapt, index) {
                    return {x: index, y: datapt.value};
                });
                data.push({
                    area: true,
                    values: values,
                    key: measure,
                });
                if (this.state.comparisonData && this.state.comparisonData.length > 0) {
                    values = this.state.comparisonData.map(function (datapt, index) {
                        return {x: index, y: datapt.value};
                    });
                    data.push({
                        values: values,
                        key: measure + ' (compare)',
                        color: '#ff7f0e',
                    });

                    if (this.state.comparisonData.length > graphData.length) {
                        tickValues = this.state.comparisonData.map(function (d, i) {
                            return i;
                        });
                    }
                }

                if (!tickValues) {
                    tickValues = graphData.map(function (d, i) {
                        return i;
                    });
                }

                var ticksLabels = [];
                for (i = 0; i < graphData.length; i++) {
                    ticksLabels.push(graphData[i].labels);
                }
                if (this.state.comparisonData && this.state.comparisonData.length > this.state.data.length) {
                    var diff = this.state.comparisonData.length - this.state.data.length;
                    var length = self.state.data.length
                    var diffTime = 0;
                    if (length < self.state.data.length) {
                        var date1 = moment(self.state.data[length - 1].labels[0]);
                        var date2 = moment(self.state.data[length - 2].labels[0]);
                        diffTime = date1 - date2;
                        for (i = 0; i < diff; i++) {
                            var value = moment(date1).add(diffTime + i * diffTime).format('DD MMM YYYY');
                            ticksLabels.push([value]);
                        }
                    }
                }

                tickFormat = function (d) {
                    return ticksLabels[d];
                };
            } else if (this.state.groupedBy.length > 1) {
                var data_dict = {};
                var tick = 0;
                var tickLabels = [];
                var serie, tickLabel;
                var identity = function (p) {
                    return p;
                };
                tickValues = [];
                for (var i = 0; i < this.state.data.length; i++) {
                    if (graphData[i].labels[0] !== tickLabel) {
                        tickLabel = this.state.data[i].labels[0];
                        tickValues.push(tick);
                        tickLabels.push(tickLabel);
                        tick++;
                    }
                    serie = graphData[i].labels[1];
                    if (!data_dict[serie]) {
                        data_dict[serie] = {
                            values: [],
                            key: serie,
                            area: true,
                        };
                    }
                    data_dict[serie].values.push({
                        x: tick - 1, y: graphData[i].value,
                    });
                    data = _.map(data_dict, identity);
                }
                tickFormat = function (d) {
                    return tickLabels[d];
                };
            }
            var $svgContainer = $('<div/>', {class: 'o_graph_svg_container'});
            this.$el.append($svgContainer);
            var svg = d3.select($svgContainer[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(0);
            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.lineChart();
            chart.options({
                margin: {left: 80, bottom: 100, top: 80, right: 80},
                useInteractiveGuideline: true,
                showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                showXAxis: true,
                showYAxis: true,
                wrapLabels: true,
                color: colors,
            });
            chart.xAxis.tickValues(tickValues)
                    .tickFormat(tickFormat);
            chart.yAxis.tickFormat(function (d) {
                return field_utils.format.float(d, {
                    digits: self.state.fields[self.state.measure] && self.state.fields[self.state.measure].digits || [69, 2],
                });
            });

            chart(svg);
            return chart;
        },
    });
});
