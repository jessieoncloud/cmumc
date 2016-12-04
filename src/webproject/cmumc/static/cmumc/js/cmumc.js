$(document).ready(function() {

	updateNavColor();
	displayRating();

	// Create_post: Datepicker
	//   http://stackoverflow.com/questions/20700185/how-to-use-datepicker-in-django
	$('.datepicker').datepicker();

	$('[data-toggle="tooltip"]').tooltip(); 
	
	$('.mode_option').click(modeEnter);

	$('#switch_btn').click(modeSwitch);
	
	$('#landing_tour').click(tour);

	$('#stream_tour').click(tour_stream);

	// Search posts ajax
	$('#search_form').on('submit', function(event) {
		event.preventDefault();
		var searchform_data = $('#search_form').serializeArray();
		$.post("/cmumc/search_post", searchform_data)
		.done(function(data) {
			$('.stream-container-messages').remove();
			getUpdates(data);
			if (data.messages) {
				var new_msg = $('<div class="stream-container-messages"> \
			            			<p class="message">' + data.messages + '</p> \
			                    </div>');
				$('.stream-container').append(new_msg);
			}
		})
	});

	// Filter available posts only ajax
	$('#available_btn').click(function(event) {
		event.preventDefault();
		var posts = getPosts();
		$.post("/cmumc/filter_available", {posts: posts})
		.done(function(data) {
			getUpdates(data);
		})
	});

	// Profile menu bar highlight
	$('.profileOpt').hover(function() {
		$(this).css("background-color", "#960000");
		$(this).find('h4').css("color", "#ffffff")
		}, function() {
		$(this).css("background-color", "#ffffff");
		$(this).find('h4').css("color", "#404040");
	});

	// Star rating
	$('.star_rating').barrating( {
	  theme: 'fontawesome-stars',
	  onSelect: function(value, text, event) {
	    if (typeof(event) !== 'undefined') {
	      // rating was selected by a user
	      console.log(event.target);
	      var rating = parseFloat($(event.target).attr('data-rating-value'));
	      console.log(rating);
	      $('#rating_score').attr('value', rating);
	    } else {
	      // rating was selected programmatically
	      // by calling `set` method
	      console.log("rated2");
	    }
	  }
	});
	
	// Filter Options
    // Price Range Input
    $("#price_range").rangeslider({
    	from: 0,
        to: 300,
        limits: false,
        step: 5,
        smooth: true,
        dimension: '$',
        onstatechange: function(value) {
        	filterAjax();
        }
    });

    // Price Range Input
    //   https://egorkhmelev.github.io/jslider/
    $("#time_range").rangeslider({
    	from: 0,
        to: 1425,
        limits: false,
        step: 15,
        smooth: true,
        dimension: '',
		calculate: function( value ){
			var hours = Math.floor( value / 60 );
			var mins = ( value - hours*60 );
			return (hours < 10 ? "0"+hours : hours) + ":" + ( mins == 0 ? "00" : mins );
		},
		onstatechange: function(value) {
			filterAjax();
		}
    });

    // Tasktype is clicked
    $('.sidebar-option-tasktype').click(filterAjax);

    // Date is clicked
    $('.sidebar-option-date').click(function() {
    	// Uncheck all of the dates
    	$('.sidebar-option-date').css("color", "#8e8071");
    	$('.sidebar-option-date').attr("checked", false);
    	// Check the date clicked
    	$(this).css("color", "#960000");
    	$(this).attr("checked", true);
    	filterAjax();
    })
}); 

function tour() {
	var tour = new Tour({
		storage: true
	});
 
	tour.addSteps([
	  {
		element: "#landing_tour",
		placement: "bottom",
		title: "Welcome to CMUMC!",
		content: "This tour will guide you through some of the features we'd like to point out."
	  },
	  {
		element: ".tour-helper",
		placement: "bottom",
		title: "Become a Helper!",
		content: "You can enter into either the helper or receiver mode. In the helper mode, you can view and accept posts created by other receivers."
	  },
	  {
		element: ".tour-receiver",
		placement: "bottom",
		title: "Become a Receiver!",
		content: "In the receiver mode, you can view and accept posts created by other helpers."
	  },
	  {
        element: ".tour-register",
        placement: "bottom",
        title: "Thank you!",
        content: "Register now and choose a mode to enter! Hope you enjoy it!"
      },
	]);
 
	// Initialize the tour
	tour.init();
	tour.start();
}

function tour_stream() {
	var tour = new Tour({
		storage: false
	});
	var usertype1;
	var usertype2;

	var usertype = $('#switch_btn').attr("value");
	console.log(usertype);
	if (usertype == "R") {
		usertype1 = "receiver";
		usertype2 = "helper";
	} else {
		usertype1 = "helper";
		usertype2 = "receiver";
	}
 
	tour.addSteps([
	  {
		element: "#stream_tour",
		placement: "bottom",
		title: "Welcome to CMUMC!",
		content: "This tour will navigate you through CMUMC."
	  },
	  {
		element: ".stream_tour_posts",
		placement: "bottom",
		title: "View a List of Posts",
		content: "This is the main page of CMUMC. You entered into the " + usertype1 + " mode and now can see a list of posts created by other " + usertype2 + "s."
	  },
	  {
		element: ".stream_tour_mode",
		placement: "bottom",
		title: "Swtich Mode",
		content: "You can switch to the " + usertype2 + " mode by clicking here. You will be able to see posts created by " + usertype1 + "s in that mode."
	  },
	  {
        element: ".stream_tour_task",
        placement: "bottom",
        title: "My Task",
        content: "You can see a list of " + usertype1 + " posts created by yourself and " + usertype2 + " posts created by others in myTask page. You can perform operations like accepting a requester, completing and rating a task there."
      },
      {
        element: ".stream_tour_username",
        placement: "left",
        title: "User Options",
        content: "You can click to view and edit profile, change password and logout. Be sure to complete your profile information before you start using the site!"
      },
	]);
 
	// Initialize the tour
	tour.init();
	tour.start();
}

// Enter a mode
function modeEnter() {
	var user_type = $(this).attr('value');
	console.log("user type: "+user_type);
	// Submit the corrsponding form
	if (user_type == 'H') {
		$('.form-mode-H').submit();
	} else if (user_type == 'R') {
		$('.form-mode-R').submit();
	}		
}

// Switch mode
function modeSwitch() {
	var username = $('#nav-username').attr("value");
	var usertype = $('#switch_btn').attr("value");

	$.post("/cmumc/switch", {mode_username: username, mode_usertype: usertype})
	.done(function(data) {
		console.log("switch ajax done!");
		console.log(data);
		$('#switch_btn').attr('value', data.usertype);
		updateNavColor();
		// updateUserTypeDisplay();
		// If the current page is the following, refresh
		var url = document.URL;
		var regStream = new RegExp("stream$");
		var regMyTask = new RegExp("mytask$");
		var regProfile = new RegExp("profile");
		var regCreatePost = new RegExp("send_post$");
		var regViewPost = new RegExp("view_post");
		var regSearch = new RegExp("search_post");
		var regFilterAvailable = new RegExp("filter_available$");
		console.log(regMyTask.test(url));
		if (regStream.test(url) || regMyTask.test(url) || regProfile.test(url) || regCreatePost.test(url) || regViewPost.test(url) || regSearch.test(url) || regFilterAvailable.test(url)) {
			location.reload();
		}
	});		
}

// Display star rating
function displayRating() {
	// Clear the rating
	$('.profile_star').empty();
	// Append the star display according to the value
	$('.profile_star').map(function() {
		var value = $(this).attr('value');
		console.log(value);
		$(this).append('<select class="profile_star_rating">');
		for (i=1; i<6; i++) {
			$(this).find('.profile_star_rating').append('<option value="'+i+'">'+i+'</option>');
		}
		$(this).append('</select>');

		$(this).find('.profile_star_rating').barrating( {
		  theme: 'fontawesome-stars-o',
		  readonly: true,
		  initialRating: value,
		});
	})
}

// Change navtop color based on user type
function updateNavColor() { 
	if ($('#switch_btn').attr('value')) {
		var user_type = $('#switch_btn').attr('value');
	}
	// console.log("user type: "+user_type);
	if (user_type == 'R') {
		$('.topnav').css("background-color", "#e1932d");
		$('#logo').css("color", "#ffffff");
		$('.topnavOptions').css("color", "#ffffff");
		$('.topnavOptions').css("background-color", "#e1932d");
		$('.navbar-fixed-top').css("border-color", "#e1932d");
		$('.topnavOptions').hover(function() {
			// hover color
			$(this).css("background-color", "#ebb670");
			}, function() {
			$(this).css("background-color", "#e1932d");
		});
	} else if (user_type == 'H') {
		$('.topnav').css("background-color", "#960000");
		$('#logo').css("color", "#fff");
		$('.topnavOptions').css("color", "#fff");
		$('.topnavOptions').css("background-color", "#960000");
		$('.navbar-fixed-top').css("border-color", "#960000");
		$('.topnavOptions').hover(function() {
			// hover color
			$(this).css("background-color", "#ff4747");
			}, function() {
			$(this).css("background-color", "#960000");
		});
	}
}

// Filter check and ajax to backend
function filterAjax() {
	var filtered = {tasktype:[], date:null, time:[], price:[]};

	// Get the filtered tasktype
	var tasktype = $('.sidebar-option-tasktype').filter(':checked');
	for (i=0; i<tasktype.length; i++) {
		filtered.tasktype[i] = tasktype[i].value;
	} 
	// Get the filtered date
	//   http://stackoverflow.com/questions/33023806/typeerror-1-attr-is-not-a-function
	//   use eq(i) instead of [i]
	var date = $('.sidebar-option-date');
	for (i=0; i<date.length; i++) {
		if (date.eq(i).attr("checked") == "checked") {
 			filtered.date = date.eq(i).attr("value");  			
		}
	} 
	// Get the filtered time
	var time = $('#time_range');
	var checked_time = time[0].value.split(";");
	filtered.time[0] = Math.floor(checked_time[0]/60);   // start time hour
	filtered.time[1] = checked_time[0]%60;   // start time min
	filtered.time[2] = Math.floor(checked_time[1]/60);   // end time hour
	filtered.time[3] = checked_time[1]%60;   // end time min
	// console.log(filtered.time);

	// Get the filtered price
	var price = $('#price_range');
	var checked_price = price[0].value.split(";");
	filtered.price[0] = checked_price[0];  // start price
	filtered.price[1] = checked_price[1];  // end price
	// console.log(filtered.price);
	
	// filter options result  
	console.log(filtered);  

	// Ajax to backend
	$.post("/cmumc/filter_post", {tasktype: filtered.tasktype, date: filtered.date, time: filtered.time, price: filtered.price})
	.done(function(data) {
		getUpdates(data);
	});
}

function getPosts() {
	var posts_id = [];
	var posts = $('.post_content');
	for (i = 0; i < posts.length; i++) {
		posts_id[i] = parseInt(posts[i].id);
	}
	return posts_id;
}

function getUpdates(data) {
	console.log("getupdates");
	var list = $(".posts");
	list.empty();
	for (var i = 0; i < data.data.length; i++) {
		var post = data.data[i];
		var new_post = $('<div class="row row-post"> \
            			<div class="col-mid-3 col25 post_img"> \
            				<img src="/cmumc/post_photo/' + post.post_id + '" class="img-rounded img-responsive post_photo"> \
            			</div> \
           				<div class="col-mid-3 col75"> \
           					<div class="col-mid-9 col75 post_content" id="' + post['post_id'] + 'post"> \
           						<a href="/cmumc/view_post/' + post.post_id + '"><h3>' + post.title + '</h3></a> \
           						<p>Time: ' + post.time + '</p> \
           						<p>Date: ' + post.date + '</p> \
           						<p>Posted by: ' + post.username + '</span></p> \
           					</div> \
       						<div class="col-mid-3 col25"> \
       							<h1>$' + post.price + '</h1> \
           					</div> \
            			</div> \
                    </div>');
		list.append(new_post);
	}
}

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
