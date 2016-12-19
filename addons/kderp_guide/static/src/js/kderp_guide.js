openerp.kderp_guide = function(instance) {
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	/*them menu kderp guide  trong menu Administrator */
	instance.web.UserMenu = instance.web.UserMenu.extend({
		on_menu_guide: function() {
			console.log('Kderp Guide');
		        window.open('kderp_guide/static/doc/index.html', '_blank');
		    },
		
		
	})
} 
