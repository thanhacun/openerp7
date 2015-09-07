
openerp.kderp_guide = function(session) {
  

  session.web.UserMenu = session.web.UserMenu.extend({
	 
	    on_menu_guide: function() {
	        window.open('kderp_guide/static/doc/index.html', '_blank');
	    },
	    
	  
  });
}

