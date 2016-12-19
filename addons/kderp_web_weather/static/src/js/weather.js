openerp.kderp_web_weather = function(instance) {
  var QWeb = instance.web.qweb;
  var API = instance.web.api;
  //inherit UserMenu widget
  instance.web.UserMenu.include ({
      init: function(parent) {
        var self = this;
        this._super.apply(this, arguments);
      },
      start: function(){
        var self = this;
        var curWeather = new kderp_weather(this);
        curWeather.prependTo(this.$el);
        return this._super();
      },
  });

  kderp_weather = instance.web.Widget.extend({
    //template: 'kderp_weather' - DO NOT use template to render QWeb with asynchronous values
    init: function(parent){
      this._super(parent);
      this.parent = parent ? true: false;
      this.interval = 60 * 60 * 1000;
    },
    className: 'kderp_weather',
    start: function(){
      var self = this;
      this._super.apply(this, arguments);
      this.bindEvents(false);
      setInterval(function(){
          console.log(new Date().toLocaleString(), "Auto refresh every", self.interval / 1000 / 60, "minutes");
          self.bindEvents(true);
      }, self.interval);
      return this._super();
    },
    curWeather: function(cb) {
      //return weather object for use with widget
      //getting forecast for chance of rain...
      API.curLoc(function(location) {
        API.weather(location.lat, location.lon, function(weather){
          return cb(weather);
        });
      });
    },
    bindEvents: function(isRefresh) {
      //bind events considering the widget will act alone or inside another widget
      var self = this;
      this.curWeather(function(res) {
          var $curWeather = $(QWeb.render('kderp_weather', {weather: res}));

          //Check widget exist or not to keep DOM tidy
          //isRefresh ? console.log(self.$el.find(".kderp_weather div").replaceWith("Hello")): self.$el.append($curWeather);
          isRefresh ? self.$el.html($curWeather): self.$el.append($curWeather);
          var bindWidget = self.parent ? self.getParent().$(".kderp_weather"): self.$(".kderp_weather");

          //prepare for tipsy content
          var onHoverContent = $(QWeb.render('kderp_weather_detail', {weather: res})).html();
          bindWidget.find("div")
              .tipsy({html: true, fade: true, gravity: "n", offset: 10, className: "tipsy_weather"})
              .attr("original-title", onHoverContent);

          //show tipsy if click to update by check hover event and isRefresh
          //using $("#element:hover").length to determine hover event happen
          if (isRefresh && bindWidget.parent().find(".kderp_weather:hover").length != 0)  {
              console.log('Mouse is on, show updated tipsy!');
              bindWidget.find("div").tipsy("show");
          };

          //bind event once
          bindWidget.unbind("click");
          bindWidget.on('click', function(ev) {
              ev.stopPropagation();
              //hide tipsy, will show again when update finished
              bindWidget.find("div").tipsy("hide");
              self.bindEvents(true);
          });
      });
    },
  })

  //Client actions
  //instance.web.client_actions.add('example.action', 'instance.web_example.Action');
}
