var deleteRun = function () {
	var	run_id = $('#delete_run_id').val();
	$.getJSON('/delete/'+run_id, function(data){
    location.reload();
  })
};

var deleteConfig = function () {
	var	task_id = $('#delete_task_id').val();
	console.log(task_id);
	$.getJSON('/delete_conf/'+task_id, function(data){
		console.log(data);
    // location.reload();
  })
};

var copyRunDir = function(run_dir){
 if (run_dir){
   alert("Run diretory: "+run_dir);
 }
};

var deleteExp = function () {
	var	exp_id = $('#delete_exp_id').val();
	$.getJSON('/deleteexp/'+exp_id, function(data){
    location.reload();
  })
};

var deletePaper = function () {
	var	paper_id = $('#delete_paper_id').val();
	$.getJSON('/deletepaper/'+paper_id, function(data){
    location.reload();
  })
};

var stopRun = function () {
	var	run_id = $('#stop_run_id').val();
	$.getJSON('/stop/'+run_id, function(data){
		if (data)
		{
      location.reload();
		}else{
			alert("The process has already stopped."); 
      location.reload();
		}
  })
};

var rescheduleRun = function () {
	var	run_id = $('#rescheduler_run_id').val();
	$.getJSON('/reschedule/'+run_id, function(data){
    location.reload();
  })
};

var addRun = function () {
	var	task_id = $('#add_run_id').val();
	$.getJSON('/add_run/'+task_id, function(data){
    location.reload();
  })
};

var editConfig = function () {
	var form = $('#config-form');
  $.post('/edit_task',
         form.serialize(),
         function(data, status, xhr){  
           if (data){ 
						  // alert("Updated!");
              location.reload();
					 }
         }
        )
}

var editPaper = function () {
	var form = $('#edit-paper-form');
  $.post('/edit_paper',
         form.serialize(),
         function(data, status, xhr){  
           if (data){ 
						  // alert("Updated!");
              location.reload();
					 }
         }
        )
}


var editRun = function () {
	var form = $('#edit-run-form');
  $.post('/edit_run',
         form.serialize(),
         function(data, status, xhr){  
           if (data){ 
						  // alert("Updated!");
              location.reload();
					 }
         }
        )
}



var addLit = function () {
	var form = $('#lit-form');
  $.post('/addlit',
         form.serialize(),
         function(data, status, xhr){  
           if (data){ location.reload(); }
         }
        )
  
}

var addConfig = function () {
	var form = $('#addconfig-form');
  $.post('/addconfig',
         form.serialize(),
         function(data, status, xhr){  
           if (data){ console.log(data); location.reload(); }
         }
        )
  
}

var recoverRun = function () {
	var	run_id = $('#recover_run_id').val();
	$.getJSON('/recover/'+run_id, function(data){
		if (data)
		{
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

var deleteConfValues = function (ID) {
		$('#delete_task_id').val(ID);
};

var editValues = function (task_id) {
		$('#edit_config_id').val(task_id);
    var form_html = "<input class='form-control mb-2 mr-sm-2' type='text' name='task_id' value='"+task_id+"' hidden>";
    $.getJSON('/taskinfo/'+task_id, function(data){
				var setting;
				for (setting in data){
			    form_html =	form_html + "<label for='"+setting+"' class='mr-sm-2'>"+setting+":</label>"+"<textarea class='form-control mb-2 mr-sm-2' name='"+setting+"'>"+data[setting]+"</textarea>"
				}
		    $('#config-form').html(form_html);
		});
};

var editPaperValues = function (paper_id) {
		$('#edit_paper_id').val(paper_id);
    var form_html = "<input class='form-control mb-2 mr-sm-2' type='text' name='paper_id' value='"+paper_id+"' hidden>";
    $.getJSON('/paperinfo/'+paper_id, function(data){
				var setting;
				for (setting in data){
			    form_html =	form_html + "<label for='"+setting+"' class='mr-sm-2'>"+setting+":</label>"+"<textarea class='form-control mb-2 mr-sm-2' name='"+setting+"'>"+data[setting]+"</textarea>"
				}
		    $('#edit-paper-form').html(form_html);
		});
};

var deletePaperValues = function (paper_id) {
		$('#delete_paper_id').val(paper_id);
};

var editRunValues = function (run_id) {
		$('#edit_run_id').val(run_id);
    var form_html = "<input class='form-control mb-2 mr-sm-2' type='text' name='run_id' value='"+run_id+"' hidden>";
		// console.log('Edit run '+ run_id)
    $.getJSON('/runinfo/'+run_id, function(data){
				var setting;
				for (setting in data){
			    form_html =	form_html + "<label for='"+setting+"' class='mr-sm-2'>"+setting+":</label>"+"<textarea class='form-control mb-2 mr-sm-2' name='"+setting+"'>"+data[setting]+"</textarea>"
				}
		    $('#edit-run-form').html(form_html);
		});
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


$( document ).ready(function() {
		var side_menu = $("#side-main-menu").find( "li" );
		var url = window.location.href.split('/');
		var loc = url[url.length-1]
		
		side_menu.each(function(index, value){
		  href = $(value).find('a').attr('href');
		  if ( href.includes(loc) )
		  {
		  	$(value).addClass( "active" );
		  }
		});
});

