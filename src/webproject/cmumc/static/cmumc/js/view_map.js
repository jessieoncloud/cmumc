$(document).ready(function() {
	console.log("view_map.js");
	// Get the latitude and longitude value
	var geo = $('#view_post_location').attr('value').split(',');
	var latitude = parseFloat(geo[0]);
	var longitude = parseFloat(geo[1]);

	var map;

	function initialize() {
		var mapDiv = $('#map-canvas');
		map = new google.maps.Map(mapDiv, {
		  center: new google.maps.LatLng(latitude, longitude),
		  zoom: 12,
		  mapTypeId: google.maps.MapTypeId.ROADMAP
		});

		google.maps.event.addListenerOnce(map, 'tilesloaded');
	}

	// function addMarkers() {
	// 	var point = new google.maps.LatLng({{mark.position.latitude}},{{mark.position.longitude}});
	// 	    var image = '{{ STATIC_PREFIX }}'+ 'checkmark.png';
	// 	    var marker = new google.maps.Marker({
	// 	    position: point,
	// 	    map: map,
	// 	    icon: image, 
	// 	    url: 'http://172.16.0.101:8882/zone/' + {{mark.id}},
	// 	   title: '{{ mark.id }}',
	// 	});
	// 	     marker['infowindow']  = new google.maps.InfoWindow({
	// 	             content: "<h1>{{mark.name}}</h1> <br> {{ mark.name }} <p> <a href=\"http:\/\/172.16.0.101:8882\/zone\/{{ mark.id }}\"> {{ mark.name }}</a>",
	// 	});
	// 	    google.maps.event.addListener(marker, 'click', function() {
	// 	        //window.location.href = this.url;
	// 	         this['infowindow'].open(map, this);
	// 	    });
	// 	   google.maps.event.addListener(marker, 'mouseover', function() {
	// 	        // this['infowindow'].open(map, this);
	// 	            });
	// 	   google.maps.event.addListener(marker, 'mouseout', function() {
	// 	        // this['infowindow'].close(map, this);

	// 	    });
	// }

	google.maps.event.addDomListener(window, 'load', initialize);
});

