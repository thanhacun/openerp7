openerp.kderp_guide = function(instance) {
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	instance.web.UserMenu = instance.web.UserMenu.extend({
		on_menu_guide: function() {
			console.log('HELLO');
		        window.open('kderp_guide/static/doc/index.html', '_blank');
		    },
		    

		/*on_menu_upload: function() {
			        window.open('kderp_guide/static/doc/file_upload.html', '_blank');
		},
		
		uploadFiles: function (){

			// Create a new HTTP requests, Form data item (data we will send to the server) and an empty string for the file paths.
			xhr = new XMLHttpRequest();
			data = new FormData();
			paths = "kderp_guide/static/doc";
			
			// Set how to handle the response text from the server
			xhr.onreadystatechange = function(ev){
				console.debug(xhr.responseText);
			};
			
			// Loop through the file list
			for (var i in files){
				// Append the current file path to the paths variable (delimited by tripple hash signs - ###)
				paths += files[i].webkitRelativePath+"###";
				// Append current file to our FormData with the index of i
				data.append(i, files[i]);
			};
			// Append the paths variable to our FormData to be sent to the server
			// Currently, As far as I know, HTTP requests do not natively carry the path data
			// So we must add it to the request manually.
			data.append('paths', paths);
				
			// Open and send HHTP requests to upload.php
			xhr.open('POST', "upload.php", true);
			xhr.send(this.data);
		}*/
		
	})
} 
