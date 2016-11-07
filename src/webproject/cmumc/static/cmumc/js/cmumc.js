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


	// // CSRF set-up copied from Django docs
	// function getCookie(name) {  
	// var cookieValue = null;
	// if (document.cookie && document.cookie != '') {
	//     var cookies = document.cookie.split(';');
	//     for (var i = 0; i < cookies.length; i++) {
	//         var cookie = jQuery.trim(cookies[i]);
	//         // Does this cookie string begin with the name we want?
	//         if (cookie.substring(0, name.length + 1) == (name + '=')) {
	//             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	//             break;
	//         }
	//     }
	// }
	// return cookieValue;
	// }
	// var csrftoken = getCookie('csrftoken');
	// $.ajaxSetup({
	// beforeSend: function(xhr, settings) {
	//     xhr.setRequestHeader("X-CSRFToken", csrftoken);
	// }
	
});