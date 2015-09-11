openerp.kderp_guide = function(session) {
	var QWeb = session.web.qweb;
	var _t = session.web._t;
	session.web.UserMenu = session.web.UserMenu.extend({
		  on_menu_help: function() {
		        window.open('kderp_guide/static/doc/index.html', '_blank');
		    },
	  });
	  
}
