var deleteRun = function () {
	var	run_id = $('#run_id').val();
	console.log('Delete '+ run_id);
	$.getJSON('/delete/'+run_id, function(data){
    console.log(data);
    location.reload();
  })
};

var values = function (ID) {
		$('#run_id').val(ID);
};
