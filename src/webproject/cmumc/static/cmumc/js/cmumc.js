$(document).ready(function() {

	console.log("here");

	// // Mode 
	// $('.mode_option').click(function() {
	// 	var user_type = $(this).attr('value');
	// 	console.log("user type: "+user_type);

	// 	// ajax sent to back end
	// 	$.post("/cmumc/mode", user_type)
	// 	.done(function(data){
	// 		alert("You've entered as a "+data.mode);
	// 	});
	// })


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