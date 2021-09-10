odoo.define('live_sale_statistic.saleStatistic', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var field_utils = require('web.field_utils');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var QWeb = core.qweb;

var yVal = 100;
var minuteInterval = 1;
var chart;
var sin = [];
var chartValues = [{
    "key": "Order's Total Amount",
    "area": true,
    "color": "#6495ED",
    "values": []
  }];

var Statistic = AbstractAction.extend(ControlPanelMixin, {
    template: 'LiveSaleStatistic',
    
    cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
    
    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['LiveSaleStatistic'];
    },

    willStart: function() {
       var self = this;
       return $.when(ajax.loadLibs(this), this._super()).then(function() {
           return self.get_order();
       });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.getRealTimeData();
        });
    },
    
    get_order: function(event) {
        var self = this;
        this._rpc({
                model: 'sale.order',
                method: 'getOrderAmount',
                args: [0],
            })
            .then(function (result) {
            	if(result){
            		self.render_graphs(result);
            	}
            	
            });
        
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_statistic_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },

    render_graph: function(div_to_display, chart_values) {
    	$('.o_cp_left').hide();
    	$('.o_cp_right').hide();
        this.$(div_to_display).empty();
        var self = this;
        nv.addGraph(function() {
            chart = nv.models.lineChart()
			            .x(function (d) { return d.x })
			            .y(function (d) { return d.y })
			            .forceY([0]);
            chart.brushExtent([50,70]);
            chart
            	.margin({left: 80, right: 50})
                .useInteractiveGuideline(true)
                .showLegend(false)
                .showYAxis(true)
                .showXAxis(true);
            
            var tick_values = self.getPrunedTickValues(chart_values[0].values, 5);
            
            chart.xAxis 
	            .axisLabel('Time (h:m)')
	            .tickFormat(function(d) {	   
	      		      return d3.time.format('%H:%M %p')(new Date(d*1000))
	      		    });
            
            chart.yAxis 
	            .tickFormat(d3.format('.02f'));

            var svg = d3.select(div_to_display)
                .append("svg");

            svg
                .attr("height", '38em')
                .datum(chart_values)
                .call(chart);
            
            nv.utils.windowResize(chart.update);
            return chart;
        });
    },
    updateChart: function(){
    	var self = this;
        this._rpc({
                model: 'sale.order',
                method: 'getOrderAmount',
                args:[minuteInterval],
            })
            .then(function (result) {
            	if(result){
            		var oldVal = chartValues[0].values;
            		oldVal.shift();
            		var lstIndx = result[result.length - 1];
            		oldVal.push(lstIndx);
                    chartValues[0].values = oldVal;
                    self.redraw_graph();
            	}
            	
            });
        minuteInterval = minuteInterval + 1;
    },
    getRealTimeData: function(){
    	var self = this;
    	setInterval(function () {
    		self.updateChart()
            
        }, 6000);
    },
    redraw_graph:function(){
    	var svg = d3.select('.o_graph_linechart svg')
    	svg
	        .attr("height", '38em')
	        .datum(chartValues)
	        .call(chart);
    },
    render_graphs: function(data) {
        var self = this;
	    chartValues[0].values = data;
        self.render_graph('.o_graph_linechart', chartValues);
    },
    
    getDate: function(d) { return new Date(d[0]); },
    getValue: function(d) { return d[1]; },
    getPrunedTickValues: function(ticks, nb_desired_ticks) {
        var nb_values = ticks.length;
        var keep_one_of = Math.max(1, Math.floor(nb_values / nb_desired_ticks));

        return _.filter(ticks, function(d, i) {
            return i % keep_one_of === 0;
        });
    },

});

core.action_registry.add('live_sale_statistic', Statistic);

return Statistic;
});