$(document).ready(function() {

	console.log("here");

	// Mode 
	$('.mode_option').click(function() {
		var user_type = $(this).attr('value');
		console.log("user type: "+user_type);

		// ajax sent to back end
		$.post("/cmumc/mode", user_type)
		.done(function(data){
			alert();
		});
	})

})