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
        center:new google.maps.LatLng(38.0329173,-78.506895),
        zoom:17,
        disableDefaultUI: true
    };
    var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
    const fetchMarker = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.iconarchive.com%2Fshow%2Fflat-vector-map-marker-icons-by-icons-land%2FMarker-1-PushPin-Green-icon.html&psig=AOvVaw0kjx0T3hNxydszdRfD3_e2&ust=1740326186800000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCJjFn7PS14sDFQAAAAAdAAAAABAl'
    /**
    *Loop through all markers and add it to the current map
    */
    for (let i = 0; i<markers.length; i++){
        const marker = new google.maps.Marker({
        position: { lat: markers[i].lat, lng:markers[i].lng},
        map:map,
        icon: fetchMarker.
        title: markers[i].locationName
    })
    }


}

