var deleteRun = function () {
	var	run_id = $('#delete_run_id').val();
	console.log('log delete '+ run_id);
	$.getJSON('/delete/'+run_id, function(data){
    console.log(data);
    location.reload();
  })
};

var rescheduleRun = function () {
	var	run_id = $('#rescheduler_run_id').val();
	console.log('log reschedule '+ run_id);
	$.getJSON('/reschedule/'+run_id, function(data){
    console.log(data);
    location.reload();
  })
};

var addRun = function () {
	var	task_id = $('#add_run_id').val();
	console.log('log add run '+ task_id);
	$.getJSON('/add_run/'+task_id, function(data){
    console.log(data);
    location.reload();
  })
};


var deleteValues = function (ID) {
		$('#delete_run_id').val(ID);
};

var rescheduleValues = function (ID) {
		$('#rescheduler_run_id').val(ID);
};

var addrunValues = function (ID) {
		$('#add_run_id').val(ID);
};

var compareRuns = function(){
		var checkedBoxes = document.querySelectorAll('input[name=compare-runs-checkbox]:checked');
		if (checkedBoxes.length >= 2) 
		{ 
			 var i;
			 var ids = new Array();
			 for (i=0; i<checkedBoxes.length; i++)
			  { 
								ids.push(checkedBoxes[i].value);
			  };
			 url = '/compare/'+ids.join('_');
			 window.location = url; 

		} else{
			 alert("Only two runs comparison are supported."); 
		};
};
