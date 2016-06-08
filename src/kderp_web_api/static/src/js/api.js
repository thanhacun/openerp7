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
        var result = res.current_observation;
        var svg_url = 'https://icons.wxug.com/i/c/v4/';
        result.svg_icon_url = svg_url + result.icon + '.svg';
        return cb(result);
      });
    }
  };

}
