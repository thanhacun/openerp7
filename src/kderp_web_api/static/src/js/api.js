openerp.kderp_web_api = function(instance) {
  //console.log("Helper functions loaded!");
  var apiURL = {
    location: 'http://ip-api.com/json',
    weather_now: 'http://thcn-api.herokuapp.com/api/weathers/now/',
    weather_hourly: 'http://thcn-api.herokuapp.com/api/weathers/hourly/'
  }
  instance.web.api = {
    curLoc: function(cb) {
      $.getJSON(apiURL.location, function(res) {
        return cb(res);
      });
    },
    weather: function(lat, lon, cb) {
      var res = {};
      //get weather condition
      $.getJSON(apiURL.weather_now + lat + ',' + lon, function(weatherNow) {
        var svg_url = 'https://icons.wxug.com/i/c/v4/';
        res.now = weatherNow.current_observation;
        res.now.svg_icon_url = svg_url + res.now.icon + '.svg';
        //get hourly forcast, only today part, flatten the return object for easily handling QWeb
        $.getJSON(apiURL.weather_hourly + lat + ',' + lon, function(weatherHourly) {
          var hourForecast = weatherHourly.hourly_forecast[0];
          res.forecast = {
            feelslike_c: hourForecast.feelslike.metric,
            humidity: hourForecast.humidity,
            uvi: hourForecast.uvi,
            pop: hourForecast.pop
          };
          return cb(res);
        });
      });
    }
  };

}
