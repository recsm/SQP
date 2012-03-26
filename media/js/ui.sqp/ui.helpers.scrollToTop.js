


//Handle an error codes returned by the server
sqpBackbone.helpers.scrollToTop = function sqpBackbone$scrollToTop(response){	
		if ($('html').scrollTop() > 100) {
				setTimeout(function(){
					$('html, body').animate({
						scrollTop: 100
					}, 300);
					
					
				}, 40);
				
				setTimeout(function() {
					$('#editCodingContainer').animate({
						backgroundColor : '#FFC18E'
					}, 300).animate({
						backgroundColor : '#fff'
					}, 600);
				}, 500);
				
			}
			
};