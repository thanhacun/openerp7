openerp.kderp_web_api = function(instance) {
  //console.log("Helper functions loaded!");
  var apiURL = {
    location: 'http://ip-api.com/json',
    weather: 'http://thcn-api.herokuapp.com/api/weathers/now/'
  }
  instance.web.api = {
    curLoc: function(cb) {
      $.getJSON(apiURL.location, function(res) {
        return cb(res);
      });
    },
    weather: function(lat, lon, cb) {
      $.getJSON(apiURL.weather + lat + ',' + lon, function(res) {
        return cb(res.current_observation);
      });
    }
  };

}
