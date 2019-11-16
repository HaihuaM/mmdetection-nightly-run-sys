/*global $, document, Chart, LINECHART, data, options, window*/
$(document).ready(function () {

    'use strict';

    // Main Template Color
    var brandPrimary = '#33b35a';
		var labels = [];
		$.getJSON('/gpu_util', function(data){
		  var hosts = data[1];
		  var devices = data[2];
		  var host_index;
		  for ( host_index in hosts)
      {
				var host = hosts[host_index]
				var chk_time = data[0][host]['chk_time'];
		    var lineChartSelector = "#lineCahrt-"+host;
        var LINECHART = $(lineChartSelector);
				var device_index;
				var dataset = new Array();
        for ( device_index in devices) 
		    {
		    	 var device_id = devices[device_index];
		  		 if ( device_id.indexOf(host) > -1 )
		  		 {
							
		    	   var load_data = data[0][host][device_id];
		    	   dataset.push({ 
												  label: device_id,
                          fill: true,
                          lineTension: 0.3,
                          backgroundColor: "rgba(77, 193, 75, 0.4)",
                          borderColor: brandPrimary,
                          borderCapStyle: 'butt',
                          borderDash: [],
                          borderDashOffset: 0.0,
                          borderJoinStyle: 'miter',
                          borderWidth: 1,
                          pointBorderColor: brandPrimary,
                          pointBackgroundColor: "#fff",
                          pointBorderWidth: 1,
                          pointHoverRadius: 5,
                          pointHoverBackgroundColor: brandPrimary,
                          pointHoverBorderColor: "rgba(220,220,220,1)",
                          pointHoverBorderWidth: 2,
                          pointRadius: 1,
                          pointHitRadius: 0,
                          data: load_data,
                          spanGaps: false
		    	               })
		  		  }
		    }

        var myLineChart = new Chart(LINECHART, {
            type: 'line',
            options: {
                legend: {
                    display: false
                }
            },
            data: {
                labels: chk_time,
                datasets: dataset
            }
          });


			}
    });

    // ------------------------------------------------------- //
    // Line Chart
    // ------------------------------------------------------ //


    // ------------------------------------------------------- //
    // Pie Chart
    // ------------------------------------------------------ //
    var PIECHART = $('#pieChart');
    var myPieChart = new Chart(PIECHART, {
        type: 'doughnut',
        data: {
            labels: [
                "First",
                "Second",
                "Third"
            ],
            datasets: [
                {
                    data: [300, 50, 100],
                    borderWidth: [1, 1, 1],
                    backgroundColor: [
                        brandPrimary,
                        "rgba(75,192,192,1)",
                        "#FFCE56"
                    ],
                    hoverBackgroundColor: [
                        brandPrimary,
                        "rgba(75,192,192,1)",
                        "#FFCE56"
                    ]
                }]
        }
    });

});
