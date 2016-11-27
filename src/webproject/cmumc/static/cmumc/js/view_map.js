$(document).ready(function() {

	// Get the latitude and longitude value
	var geo = $('#view_post_location').attr('value').split(',');
	var latitude = parseFloat(geo[0]);
	var longitude = parseFloat(geo[1]);

	var map;

	function initMap() {
		var center = {lat: latitude, lng: longitude};
		console.log(center);
		var map = new google.maps.Map(document.getElementById('map-canvas'), {
		  zoom: 17,
		  center: center
		});
		var marker = new google.maps.Marker({
		  position: center,
		  map: map
		});
	}

	initMap();
});

