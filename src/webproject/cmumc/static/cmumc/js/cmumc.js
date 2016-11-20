$(document).ready(function() {

	console.log("here");
	updateNavColor();
	// updateUserTypeDisplay();

	// Create_post: Datepicker
	//   http://stackoverflow.com/questions/20700185/how-to-use-datepicker-in-django
	$('.datepicker').datepicker();

	$('[data-toggle="tooltip"]').tooltip(); 

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


	// Switch mode ajax
	$('#switch_btn').click(function() {
		console.log("here");
		var username = $('#nav-username').attr("value");
		var usertype = $('#switch_btn').attr("value");
		console.log("username: "+username);
		console.log("usertype: "+usertype);

		$.post("/cmumc/switch", {mode_username: username, mode_usertype: usertype})
		.done(function(data) {
			console.log("switch ajax done!");
			console.log(data);
			$('#switch_btn').attr('value', data.usertype);
			updateNavColor();
			// updateUserTypeDisplay();
			// If the current page is mytask or profile, refresh
			var url = document.URL;
			var regStream = new RegExp("stream$");
			var regMyTask = new RegExp("mytask$");
			var regProfile = new RegExp("profile");
			var regCreatePost = new RegExp("send_post$");
			var regViewPost = new RegExp("view_post");
			var regSearchPost = new RegExp("search_post");
			console.log(regMyTask.test(url));
			if (regStream.test(url) || regMyTask.test(url) || regProfile.test(url) || regCreatePost.test(url) || regViewPost.test(url) || regSearchPost.test(url)) {
				location.reload();
			}
		});
	})

	// Profile menu bar highlight
	$('.profileOpt').hover(function() {
		$(this).css("background-color", "#404040");
		$(this).find('h4').css("color", "#ffffff")
		}, function() {
		$(this).css("background-color", "#ffffff");
		$(this).find('h4').css("color", "#404040");
	}) 


	// Change navtop color based on user type
	function updateNavColor() { 
		if ($('#switch_btn').attr('value')) {
			var user_type = $('#switch_btn').attr('value');
		}
		// console.log("user type: "+user_type);
		if (user_type == 'H') {
			$('.topnav').css("background-color", "#404040");
			$('#logo').css("color", "#ffffff");
			$('.topnavOptions').css("color", "#ffffff");
			$('.topnavOptions').css("background-color", "#404040");
			$('.topnavOptions').hover(function() {
				$(this).css("background-color", "#777");
				}, function() {
				$(this).css("background-color", "#404040");
			});
		} else if (user_type == 'R') {
			$('.topnav').css("background-color", "#f2f2f2");
			$('#logo').css("color", "#777");
			$('.topnavOptions').css("color", "#777");
			$('.topnavOptions').css("background-color", "#f2f2f2");
			$('.topnavOptions').hover(function() {
				$(this).css("background-color", "#ffffff");
				}, function() {
				$(this).css("background-color", "#f2f2f2");
			});
		}
	}

	// function updateUserTypeDisplay() {
	// 	if ($('#switch_btn').attr('value')) {
	// 		var user_type = $('#switch_btn').attr('value');
	// 	}
	// 	if (user_type == 'H') {
	// 		$('.user_mode').empty();
	// 		$('.user_mode').html('Helper');
	// 	}
	// 	if (user_type == 'R') {
	// 		$('.user_mode').empty();
	// 		$('.user_mode').html('Receiver');
	// 	}
	// }


	// CSRF set-up copied from Django docs
	function getCookie(name) {  
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
		    var cookies = document.cookie.split(';');
		    for (var i = 0; i < cookies.length; i++) {
		        var cookie = jQuery.trim(cookies[i]);
		        // Does this cookie string begin with the name we want?
		        if (cookie.substring(0, name.length + 1) == (name + '=')) {
		            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		            break;
		        }
		    }
		}
		return cookieValue;
		}
		var csrftoken = getCookie('csrftoken');
		$.ajaxSetup({
		beforeSend: function(xhr, settings) {
		    xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	});
	
});