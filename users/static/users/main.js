function myMap() {
    const markers = [
    {
        locationName: "Shannon Library" ,
        lat:38.0364566,
        lng:-78.5053683,
        address: '160 McCormick Rd, <br> Charlottesville, <br> VA 22904'
    },
    {
        locationName: "Rice Hall" ,
        lat:38.0316188,
        lng:-78.5196006,
        address: "85 Engineer's Way, <br> Charlottesville, <br> VA 22903"
    },
    {
        locationName: "Gibbons House" ,
        lat:38.0331636,
        lng:-78.514679,
        address: '425 Tree House Dr, <br> Charlottesville, <br> VA 22904'
    },
    {
        locationName: "Student Health and Wellness" ,
        lat:38.0301536,
        lng:-78.503874,
        address: '550 Brandon Ave, <br> Charlottesville, <br> VA 22903'
    }
    ];

    var mapProp= {
        center:new google.maps.LatLng(38.0341423,-78.5082731),
        zoom:15,
        disableDefaultUI: true,
        styles:
        [
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#e9e9e9"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f5f5f5"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 29
            },
            {
                "weight": 0.2
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 18
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f5f5f5"
            },
            {
                "lightness": 21
            }
        ]
    },
    {
        "featureType": "poi.park",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#dedede"
            },
            {
                "lightness": 21
            }
        ]
    },
    {
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#ffffff"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "saturation": 36
            },
            {
                "color": "#333333"
            },
            {
                "lightness": 40
            }
        ]
    },
    {
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f2f2f2"
            },
            {
                "lightness": 19
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#fefefe"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#fefefe"
            },
            {
                "lightness": 17
            },
            {
                "weight": 1.2
            }
        ]
    }
]
};
    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
    const fetchMarker = "https://icons.iconarchive.com/icons/icons-land/flat-vector-map-marker/48/Marker-1-PushPin-Green-icon.png";
    /**
    *Loop through all markers and add it to the current map
    */
    for (let i = 0; i<markers.length; i++){
        const marker = new google.maps.Marker({
        position: { lat: markers[i].lat, lng:markers[i].lng},
        map:map,
        icon: fetchMarker,
        title: markers[i].locationName
        });

        const infoWindow = new google.maps.InfoWindow({
            content: `<strong>${markers[i].locationName}</strong><br>${markers[i].address}`
        });

        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });

    }


}

