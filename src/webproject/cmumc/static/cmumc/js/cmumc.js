$(document).ready(function() {

	console.log("here");

	// Mode 
	$('.mode_option').click(function() {
		var user_type = $(this).attr('value');
		console.log("user type: "+user_type);

		// Submit the corrsponding form
		if (user_type == 'H') {
			$('.form-mode-H').submit();
		} else if (user_type == 'R') {
			$('.form-mode-R').submit();
		}
		
	})

	// Change navtop color based on user type
	function updateNavColor{
		var user_type = $('#switch_btn').attr('value');
		console.log("user type: "+user_type);

		if (user_type == 'H') {
			$('.topnav').css("background-color", "#404040");
		} else if (user_type == 'R') {
			$('.topnav').css("background-color", "#e7e7e7");
		}
	}
	
});