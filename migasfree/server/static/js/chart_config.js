var colors = [
    "#7cb5ec", "#434348", "#90ed7d", "#f7a35c", "#8085e9",
    "#f15c80", "#e4d354", "#2b908f", "#f45b5b", "#91e8e1",
    "#2f7ed8", "#0d233a", "#8bbc21", "#910000", "#1aadce"
];

function loadDatum(data) {
    var dataLen, i;
    var serie = [];

    dataLen = data.length;
    for (i = 0; i < dataLen; i += 1) {
        serie.push({
            name: data[i].name + " (" + data[i].value + ")",
            y: data[i].y,
            color: colors[i],
            url: data[i].url
        });
    }

    return serie;
}

function loadData(data) {
    var dataLen, drillDataLen, brightness, i, j;
    var serie1 = [], serie2 = [];

    dataLen = data.length;
    for (i = 0; i < dataLen; i += 1) {
        serie1.push({
            name: data[i].name + " (" + data[i].value + ")",
            y: data[i].y,
            color: colors[i],
            url: data[i].url
        });

        drillDataLen = data[i].data.length;
        for (j = 0; j < drillDataLen; j += 1) {
            brightness = 0.2 - (j / drillDataLen) / 5;
            serie2.push({
                name: data[i].data[j].name + " (" + data[i].data[j].value + ")",
                y: data[i].data[j].y,
                color: Highcharts.Color(colors[i]).brighten(brightness).get(),
                url: data[i].data[j].url
            });
        }
    }

    return [serie1, serie2];
}

var options = {
    credits: {
        enabled: false
    },
    chart: {
        type: "pie"
    },
    title: {
        text: null
    },
    plotOptions: {
        pie: {
            shadow: false,
            center: ["50%", "50%"]
        },
        series: {
            animation: false,
            cursor: "pointer",
            point: {
                events: {
                    click() {
                        if (typeof this.options.url !== "undefined") {
                            window.open(this.options.url, "_self");
                        }
                    }
                }
            }
        }
    },
    tooltip: {
        valueSuffix: "%",
        headerFormat: "{point.key}",
        pointFormat: ": <strong>{point.y}</strong>"
    },
    series: [{
        size: "100%",
        dataLabels: {
            formatter() {
                return this.y > 5 ? this.point.name : null;
            },
            color: "#fff",
            distance: -30
        }
    }]
};

var optionsMulti = {
    credits: {
        enabled: false
    },
    chart: {
        type: "pie"
    },
    title: {
        text: null
    },
    plotOptions: {
        pie: {
            shadow: false,
            center: ["50%", "50%"]
        },
        series: {
            animation: false,
            cursor: "pointer",
            point: {
                events: {
                    click() {
                        if (typeof this.options.url != "undefined") {
                            window.open(this.options.url, "_self");
                        }
                    }
                }
            }
        }
    },
    tooltip: {
        valueSuffix: "%",
        headerFormat: "{point.key}",
        pointFormat: ": <strong>{point.y}</strong>"
    },
    series: [{
        size: "60%",
        dataLabels: {
            formatter() {
                return this.y > 5 ? this.point.name : null;
            },
            color: "#fff",
            distance: -30
        }
    }, {
        size: "100%",
        innerSize: "60%",
        dataLabels: {
            enabled: false
        }
    }]
};

var series;
