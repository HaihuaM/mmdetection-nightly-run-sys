var deleteRun = function () {
	var	run_id = $('#delete_run_id').val();
	console.log('log delete '+ run_id);
	$.getJSON('/delete/'+run_id, function(data){
    console.log(data);
    location.reload();
  })
};

var deleteExp = function () {
	var	exp_id = $('#delete_exp_id').val();
	console.log('log delete '+ exp_id);
	$.getJSON('/deleteexp/'+exp_id, function(data){
    console.log(data);
    location.reload();
  })
};

var stopRun = function () {
	var	run_id = $('#stop_run_id').val();
	console.log('log stop '+ run_id);
	$.getJSON('/stop/'+run_id, function(data){
		if (data)
		{
      console.log(data);
      location.reload();
		}else{
			alert("The process has already stopped."); 
      location.reload();
		}
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

var editConfig = function () {
	var	task_id = $('#edit_config_id').val();
	console.log('log edit config'+ task_id);
	$.getJSON('/edit_config/'+task_id, function(data){
    console.log(data);
    // location.reload();
  })
};

var recoverRun = function () {
	var	run_id = $('#recover_run_id').val();
	console.log('log recover run '+ run_id);
	$.getJSON('/recover/'+run_id, function(data){
		if (data)
		{
      console.log(data);
      location.reload();
		}else{
		  alert("The the run must be stopped."); 
      location.reload();
		}
  })
};


var deleteValues = function (ID) {
		$('#delete_run_id').val(ID);
};

var deleteExpValues = function (ID) {
		$('#delete_exp_id').val(ID);
};

var stopValues = function (ID) {
		$('#stop_run_id').val(ID);
};

var rescheduleValues = function (ID) {
		$('#rescheduler_run_id').val(ID);
};

var addrunValues = function (ID) {
		$('#add_run_id').val(ID);
};

var editValues = function (ID) {
		$('#edit_config_id').val(ID);
};

var recoverValues = function (ID) {
		$('#recover_run_id').val(ID);
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


var addexpRuns = function(){
		var checkedBoxes = document.querySelectorAll('input[name=compare-runs-checkbox]:checked');
		if (checkedBoxes.length >= 2) 
		{ 
			 var i;
			 var ids = new Array();
			 for (i=0; i<checkedBoxes.length; i++)
			  { 
								ids.push(checkedBoxes[i].value);
			  };
			 url = '/addexp/'+ids.join('_');
			 $.getJSON(url, function(data){
					// console.log(data);
					if (data)
					{
					  location.reload();
					} else {
					  alert('Already exists.')
					}
				})

		} else{
			 alert("At least two runs comparison are supported."); 
		};
};

