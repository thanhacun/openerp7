openerp.kderp_guide = function(instance) {
	var QWeb = session.web.qweb;
	var _t = session.web._t;
	
	session.web.UserMenu = session.web.UserMenu.extend({
		init: function(parent) {
			console.log("HELLO");
			this._super(parent);
		}
		
		start: function() {
				console.log("HELO");
				this.$el.on('click', '#kdvn_guide', function(ev) {
					console.log("TESTING");
				});
			}    
		},
		on_menu_guide: function() {
		        window.open('kderp_guide/static/doc/index.html', '_blank');
		    },
    
}
