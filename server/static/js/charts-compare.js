/*global $, document, LINECHARTEXMPLE*/
$(document).ready(function () {

    'use strict';

    var brandPrimary = 'rgba(51, 179, 90, 1)';

		var url = window.location.href;
		var url_list = url.split('/');
		var compare_id = url_list[url_list.length-1];

		var range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i);
		
    $.getJSON('/compare_run_status/'+compare_id, function(data){
					var run_data = data['data'];
					var names = data['names'];
					var data_key;
					console.log(run_data);
					
					for (data_key in run_data[0])
					{
						var LINECHART   = $('#lineChart-'+data_key);
						var datasets = new Array();
						var lengths = new Array();
						var label_length;
						var backgroundColor = [
								"rgba(20, 0, 90, 0.38)",
								"rgba(51, 140, 90, 0.38)",
								"rgba(51, 179, 23, 0.38)",
								"rgba(39, 120, 25, 0.38)",
								"rgba(121, 179, 200, 0.38)",
								"rgba(36, 45, 90, 0.38)",
						];
						var borderColor = [
								"rgba(20, 0, 90, 0.38)",
								"rgba(51, 140, 90, 0.38)",
								"rgba(51, 179, 23, 0.38)",
								"rgba(51, 179, 25, 0.38)",
								"rgba(121, 179, 200, 0.38)",
								"rgba(36, 45, 90, 0.38)",
						];
						var i;
						for (i=0; i<run_data.length; i++)
						{
					    lengths.push(run_data[i][data_key].length);	
						  datasets.push({
	      				label: names[i],
	      				fill: false,
	      				lineTension: 0.3,
	      				backgroundColor: backgroundColor[i],
	      				borderColor: borderColor[i],
	      				borderCapStyle: 'butt',
	      				borderDash: [],
	      				borderDashOffset: 0.0,
	      				borderJoinStyle: 'miter',
	      				borderWidth: 1,
	      				pointBorderColor: borderColor[i],
	      				pointBackgroundColor: "#fff",
	      				pointBorderWidth: 1,
	      				pointHoverRadius: 2,
	      				pointHoverBackgroundColor: brandPrimary,
	      				pointHoverBorderColor: "rgba(220,220,220,1)",
	      				pointHoverBorderWidth: 1,
	      				pointRadius: 0.3,
	      				pointHitRadius: 1,
	      				data: run_data[i][data_key],
	      				spanGaps: false
	      				});
						}
						
						label_length = Math.max(...lengths);

						var lineChart = new Chart(LINECHART, {
								type: 'line',
								data: {
										labels: range(0, label_length),
										datasets: datasets
								}
						});

					}
    });


});
