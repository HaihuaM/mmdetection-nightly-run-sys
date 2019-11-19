/*global $, document, LINECHARTEXMPLE*/
$(document).ready(function () {

    'use strict';

    var brandPrimary = 'rgba(51, 179, 90, 1)';

		var url = window.location.href;
		var url_list = url.split('/');
		var run_id = url_list[url_list.length-1];
		var range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i);
		$.getJSON('/run_status/'+run_id, function(data){
				var datasets = {};
				for (var data_key in data)
				{
						var LINECHART   = $('#lineChart-'+data_key);

						datasets[data_key] = {
	      				label: data_key,
	      				fill: true,
	      				lineTension: 0.3,
	      				backgroundColor: "rgba(51, 179, 90, 0.38)",
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
	      				pointHitRadius: 10,
	      				data: data[data_key],
	      				spanGaps: false
	      				};

						var lineChart = new Chart(LINECHART, {
								type: 'line',
								data: {
										labels: range(0, data[data_key].length),
										datasets: [datasets[data_key]]
								}
						});
				}

		});



});
