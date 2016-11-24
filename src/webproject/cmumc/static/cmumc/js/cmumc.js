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
			// If the current page is the following, refresh
			var url = document.URL;
			var regStream = new RegExp("stream$");
			var regMyTask = new RegExp("mytask$");
			var regProfile = new RegExp("profile");
			var regCreatePost = new RegExp("send_post$");
			var regViewPost = new RegExp("view_post");
			var regSearchPost = new RegExp("search_post");
			var regFilterAvailable = new RegExp("filter_available$");
			console.log(regMyTask.test(url));
			if (regStream.test(url) || regMyTask.test(url) || regProfile.test(url) || regCreatePost.test(url) || regViewPost.test(url) || regSearchPost.test(url) || regFilterAvailable.test(url)) {
				location.reload();
			}
		});
	})

	// Profile menu bar highlight
	$('.profileOpt').hover(function() {
		$(this).css("background-color", "#960000");
		$(this).find('h4').css("color", "#ffffff")
		}, function() {
		$(this).css("background-color", "#ffffff");
		$(this).find('h4').css("color", "#404040");
	}) 

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
	
	// Filter Options
    // Price Range Input
    $("#price_range").rangeslider({
        from: 0,
        to: 300,
        limits: false,
        // scale: ['$0', '$300'],
        // heterogeneity: ['100/300'],
        step: 5,
        smooth: true,
        dimension: '$',
        onstatechange: function(value) {
        	// console.dir(this);
        	filterAjax();
        }
    });

    // Price Range Input
    //   https://egorkhmelev.github.io/jslider/
    $("#time_range").rangeslider({
        from: 0,
        to: 1425,
        limits: false,
        // scale: ['0:00', '24:00'],
        step: 15,
        smooth: true,
        dimension: '',
		calculate: function( value ){
			var hours = Math.floor( value / 60 );
			var mins = ( value - hours*60 );
			return (hours < 10 ? "0"+hours : hours) + ":" + ( mins == 0 ? "00" : mins );
		},
		onstatechange: function(value) {
			// console.dir(this);
			filterAjax();
		}
    });

    // Tasktype is clicked
    $('.sidebar-option-tasktype').click(function(){
    	filterAjax();
    });

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
			console.log("filter ajax done!");
			console.log(data);
			var list = $(".posts");
			list.empty();
			for (var i = 0; i < data.data.length; i++) {
				var post = data.data[i];
				var $new_post = $('<div class="row row-post"> \
								<div class="col-mid-3 col25 post_img"> \
									<a href="/cmumc/view_post/"' + post.post_id + '><img src="/cmumc/post_photo/' + post.post_id + '" class="img-rounded img-responsive post_photo"></a> \
								</div> \
								<div class="col-mid-3 col75"> \
									<div class="col-mid-9 col75 post_content"> \
										<a href="/cmumc/view_post/' + post.post_id + '"><h3>' + post.title + '</h3></a> \
										<p>Location: ' + post.location + '</p> \
										<p>Time: ' + post.time + '</p> \
										<p>Date: ' + post.date + '</p> \
										<p>Posted by: ' + post.username + '</p> \
									</div> \
									<div class="col-mid-3 col25"> \
										<h1>$' + post.price + '</h1> \
									</div> \
								</div> \
							</div>');
				list.append($new_post);
			}
		});
    }

	function getUpdates(data) {
		var list = $(".posts");
		list.empty();
		console.log("here");
		console.log(data)
		console.log(data.length);
		for (var i = 0; i < data.length; i++) {
			console.log("there");
			var post = data[i];
			console.log(post.post_id);
			console.log("!");
			console.log(post['post_id']);
			var $new_post = $('<div class="row row-post"> \
                			<div class="col-mid-3 col25 post_img"> \
                				<a href="/cmumc/view_post/"' + post['post_id'] + '><img src="/cmumc/post_photo/' + post.post_id + '" class="img-rounded img-responsive post_photo"></a> \
                			</div> \
               				<div class="col-mid-3 col75"> \
               					<div class="col-mid-9 col75 post_content"> \
               						<a href="/cmumc/view_post/' + post.post_id + '"><h3>' + post.title + '</h3></a> \
               						<p>Location: ' + post.location + '</p> \
               						<p>Time: ' + post.time + '</p> \
               						<p>Date: ' + post.date + '</p> \
               						<p>Posted by: ' + post.username + '></span></p> \
               					</div> \
           						<div class="col-mid-3 col25"> \
           							<h1>$' + post.price + '</h1> \
               					</div> \
                			</div> \
                        </div>');
			list.append($new_post);
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

});

