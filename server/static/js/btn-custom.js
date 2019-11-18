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

var deleteValues = function (ID) {
		$('#delete_run_id').val(ID);
};

var rescheduleValues = function (ID) {
		$('#rescheduler_run_id').val(ID);
};
