openerp.kderp_guide = function(instance) {
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	instance.web.UserMenu = instance.web.UserMenu.extend({
	/*	init: function(parent)  {
			this._super(parent);
		}, */
		on_menu_guide: function() {
			console.log('HELLO');
		        window.open('kderp_guide/static/doc/index.html', '_blank');
		    },

		/*on_menu_help: function() { 
			console.log('QUICK GUIDE');
		}
    */
})
} 
