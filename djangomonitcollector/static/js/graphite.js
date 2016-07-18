// graphite.js

(function($) {



    $.fn.dygraphite = function(options, dysettings) {
        if (options === "update") {
            $.fn.graphite.update(this, arguments[1]);
            return this;
        }

        // Initialize plugin //
        options = options || {};
        var settings = $.extend({}, $.fn.graphite.defaults, options);
        var dysettings = $.extend({}, $.fn.graphite.dydefaults, dysettings);

        return this.each(function() {
            var $this = $(this);
            $.fn.graphite.renderdy($this, settings, dysettings);
        });

    };

    $.fn.graphite = function(options) {
        if (options === "update") {
            $.fn.graphite.update(this, arguments[1]);
            return this;
        }

        // Initialize plugin //
        options = options || {};
        var settings = $.extend({}, $.fn.graphite.defaults, options);

        return this.each(function() {
            var $this = $(this);

            $this.data("graphOptions", settings);
            $.fn.graphite.render($this, settings);
        });

    };

    $.fn.graphite.geturl = function(rawOptions) {

        var src = rawOptions.url + "?";

        // use random parameter to force image refresh
        var options = $.extend({}, rawOptions);

        options["_t"] = options["_t"] || Math.random();

        $.each(options, function(key, value) {
            if (key === "target") {
                $.each(value, function(index, value) {
                    src += "&target=" + value[0];
                });
            } else if (value !== null && key !== "url" && key !== "autoupdate") {
                src += "&" + key + "=" + value;
            }
        });
        return src.replace(/\?&/, "?");
    };

    $.fn.graphite.render = function($img, options) {
        $img.attr("src", $.fn.graphite.geturl(options));
        $img.attr("height", options.height);
        $img.attr("width", options.width);
    };

    $.fn.graphite.renderdy = function($dyobj, options, dysettings) {

        dysettings.labels = []
        dysettings.labels.push($.fn.graphite.dydefaults.xlabel)

        $.each(options, function(key, value) {
            if (key === "target") {
                $.each(value, function(index, value) {
                    dysettings.labels.push(value[1])
                })
            }
        })

        options.format = 'json'
        var url = $.fn.graphite.geturl(options)
        var g

        //Get JSON data from Graphite
        $.getJSON(url, function(result) {

            var graphiteData = new Object();

            if (result.length === null || result.length === 0) {
                $dyobj.html("<div class=\"text-center\">No Data Available: Resource not monitored or Monitoring not supported</div>")
                return
            }
            $.each(result, function(i, item) {

                //fill out the array with the metrics
                $.each(item["datapoints"], function(key, val) {

                    tempDate = val[1];

                    if (!(tempDate in graphiteData)) {
                        graphiteData[tempDate] = [];
                    }

                    //I've chosen to 0 out any null values, otherwise additional data series
                    //could be inserted into previous data series array
                    if (val[0] === null) {
                        val[0] = 0;
                    }


                    graphiteData[tempDate].push([val[0]]);

                });
            });

            //need to flatten the hash to an array for Dygraph
            var dygraphData = [];

            for (var key in graphiteData) {

                if (graphiteData.hasOwnProperty(key)) {

                    tempArray = [];
                    tempArray.push(new Date(key * 1000));
                    dataSeries = graphiteData[key];

                    for (var key in dataSeries) {
                        if (dataSeries.hasOwnProperty(key)) {
                            tempArray.push(parseInt(dataSeries[key]));
                        }
                    }
                    dygraphData.push(tempArray);
                }
            }

            g = new Dygraph($dyobj.get(0), dygraphData, {
                rollPeriod: dysettings.rollPeriod,
                valueRange: dysettings.valueRange,
                legend: 'always', // show always
                labelsDivWidth: '140', // default 250
                labelsSeparateLines: true,
                ylabel: dysettings.ylabel,
                xlabel: dysettings.xlabel,
                drawPoints: dysettings.draw_point,
                errorBars: dysettings.errorbars,
                pointSize: dysettings.point_size,
                strokeWidth: dysettings.stroke_width,
                stackedGraph: dysettings.isStacked,
                axisLabelColor: '#BBB',
                axisLineColor: '#BBB',
                labels: dysettings.labels,
                labelsKMB: true,
                animatedZooms: true,
                fillGraph: true,
                //logscale: true,
                colors: dysettings.graph_colors,

                zoomCallback: function() {
                    $.fn.dygraphite.setlinewidth(g, dygraphData)
                },
            });
        });
        return g
    };



    $.fn.dygraphite.setlinewidth = function(g, data) {
        var range = g.xAxisRange();
        var data_points = 0;
        var max = 0
        for (var i = 0; i < data.length; i++) {
            var x = data[i][0];
            var y = data[i][1]
            if (x > range[0] && x < range[1])
                data_points++;
            if (y > max)
                max = max + 10

        }

        var new_opts = {};
        //   new_opts.valueRange = [null,max]
        if (data_points > 2000) {
            new_opts.pointSize = 0.5;
            new_opts.strokeWidth = 0.5;
        } else if (data_points > 900) {
            new_opts.pointSize = 1;
            new_opts.strokeWidth = 1;
        } else {
            new_opts.pointSize = 1.5;
            new_opts.strokeWidth = 1.5;
        }
        g.updateOptions(new_opts);
    }

    $.fn.graphite.update = function($img, options) {
        options = options || {};
        $img.each(function() {
            var $this = $(this);
            var settings = $.extend({}, $this.data("graphOptions"), options);
            $this.data("graphOptions", settings);
            $.fn.graphite.render($this, settings);
        });
    };

    // Default settings.
    // Override with the options argument for per-case setup
    // or set $.fn.graphite.defaults.<value> for global changes
    $.fn.graphite.defaults = {
        from: "-24hours",
        height: "300",
        until: "now",
        url: "/render/",
        width: "940",
        format: "img",
        autoupdate: 1,
    };

    $.fn.graphite.dydefaults = {
        fillGraph: true,
        labelsKMB: true,
        animatedZooms: true,
        point_size: 1,
        stroke_width: 1.5,
        rollperiod: 10,
        draw_point: false,
        isStacked: false,
        errorbars: false,
        graph_colors: ["#1ab394", "#ed5565", "#f8ac59", "#1c84c6"],
        ylabel: "Default",
        xlabel: "Date/Time",
        labels: [],
        valueRange: [null, null]
    }

}(jQuery));
