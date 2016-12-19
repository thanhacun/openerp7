openerp.kderp_web_api = function(instance) {
  //console.log("Helper functions loaded!");
  var apiURL = {
    location: 'http://ip-api.com/json',
    weather_now: 'http://thcn-api.herokuapp.com/api/weathers/now/',
    weather_hourly: 'http://thcn-api.herokuapp.com/api/weathers/hourly/',
    weather_forecast: 'http://thcn-api.herokuapp.com/api/weathers/forecast/'
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
        $.getJSON(apiURL.weather_forecast + lat + ',' + lon, function(weatherForecast) {
          var hourForecast = weatherForecast.forecast.simpleforecast.forecastday[0];
          res.forecast = {
            high_low: hourForecast.high.celsius + '/' + hourForecast.low.celsius,
            humidity: hourForecast.avehumidity,
            pop: hourForecast.pop
          };
          return cb(res);
        });
      });
    },
    userAvatar: function(uid, cb) {
      //return true if user having avatar and vice verse
        var Users = new instance.web.Model("res.users"),
            Employees = new instance.web.Model("hr.employee");
        //TODO: find another way to check default image
        var default_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAAACXZwQWcAAABAAAAAQADq8/hgAAAEWklEQVRYw9WX6XKjRhCAef8HiySQvGt5vfZuEselOUAcEpe4GdI9MAgQOjb5k3SVyzY1801PX9OtNf9StP80QJR5miRpXtb/AFCnvmMySgmhlJn2Mal+BSBSj1NCGeNSGAMOd0/iQYCI95TAXnm+FCr/I2ZYPwJILEJhPaGm7flBFIW+Z5sUvwEivguovG7pMR0cV2e+BbYArF3cBqQclKfEvryvSB2KaHa6BYhgDSP7ZN7gmUNQCf86wCdgcBaKq04/cTzAuwbA/czKb8VdZYMSI8IAEOJ+XjTiFkF4SDjOARIIHLiBK+4E/xHOIdEloMSAAwZx7hEOBKIquwA4lFPbR/3uEhzCqSUmgBiwrGgeIlQm5b0zO0CN3yKw34QgQC4JKZqrGAFC0MpWvuwJ3V6hWD3BI5wchoDaBAumzYQgmsrd7ewZx5bosHIAAAtQp4+nXUuA+2yXy9Xyi4OsIorjauBLZQWtd0Gqrt3EvCXQlb4BMZYfsPP7cr0gvS4FaNw6Qus0ovtez8DZcYyHt8Wmk9XWdF+Mjf570Ke4q46UgAgUCtX55mKl/wSbsD83hrEE0VGJ1RrEWHz2aaXuIAEe7b3SNG/601oSzL/W20/T2r2uDNACARvjWelZQTTaCiCg2vSR1bzrsFgSQMk8SbPi8FWX+0GFbX2OXMarDoAmOGfo+wpXt7cwj4Hv+1n+rSMYW3HOfS4TAgHZIDIVYG38wNzchyB+kj4ZUwB4npw6ABokmgA2qz9kfbIkoWDLzQSQ0tbw2gA20kA/nmyqCHG8nmqQd2prbSKQZAIwnk5B5PSE/EWfACCUZGFSgHQKeE6DsCcExfc5wKEDRLMaJHBwTwA/zFzhOLBBPGODoCfEyYUb0XVBB1AGHXvho/SVDsSjF15QrtMG1xlpsDbCrCewj7UxAWAJSjsAlJOuHI0AX9Mi8IMgsJnMC2MMOJA2f7RhXI8AG/2LVxZZVlQWmKElnAFiT5nMH62L67Mb3lTmbIzVK3Uc9r6GvJAEyMa6d0KXP1oXliqbRPPzN0NvBcrBAmSpr37wlrB8GeRS6zkJECZVNRKeuLfty1C+wc/zp7TD9jVQN7DUDq2vkUEzfAymIl9uZ5iL1B0U1Rw7surmc4SE/sUBE3KaDB8Wd1QS7hJQga4Kayow2aAsXiV0L458HE/jx9UbPi33CIf+ITwDSnxM/IcIcAGIrHzaH+BX8Ky4awdq41nBZYsjG4/kEQLjg9Q5A9A1jJ7u3CJEa1OzmuvSKgubwPA24IT7WT7fJ5YmEtwbASWO2AkP94871WpPOCc8vmYHaORhv5lf75VrV3bD+9nZIrUJamhXN9v9kMlu3wonYVlGe9msU1/cGTgKpx0YmO2fsrKq66rMk8Bh7dd99sDIk+xxxsE5icqhqfsLflkz1pkbukSCBzI5bqG0EGrPGvfK2FeGDseRi1I5eVFuB8WvDp51FvsH13Fcz4+y6n86Oz8kfwPMD02INEiadQAAAABJRU5ErkJggg=="
        Users.query([])
            .filter([['id','=',uid]])
            .first().then(function(cur_user){
                //console.log(cur_user);
                Employees.query([])
                    .filter([['id', '=', cur_user.employee_id[0]]])
                    .first().then(function(cur_employee) {
                        return cb(cur_employee.image !== default_image_base64);
                    });
            });
    }
  };

}
