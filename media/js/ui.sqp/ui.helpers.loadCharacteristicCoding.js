// Load a Characteristic
// Acutally this always loads the next characteristic by using
// a characteristic from id, so we don't know what
// characteristic is being loaded until we get the resonse back form the server
sqpBackbone.helpers.loadCharacteristicCoding = function sqpBackbone$loadCharacteristicCoding(characteristicURL, completionId){
	var characteristicCoding = new sqpBackbone.models.characteristicItem;
	characteristicCoding.url = characteristicURL;
	characteristicCoding.fetch({
		success: function(response){
			//alert("success" + JSON.stringify(msg));
			// update the HTML fragment without triggering our controller
			
			if(completionId) {
				if(response.toJSON().characteristicShortName == 'complete') {
					$('.editCodingLoading').hide();
				} else {
					window.location.hash = "#characteristic/" 
									+ response.toJSON().characteristicId 
									+"/question/" 
									+ response.toJSON().questionId
									+ '/' + completionId;
				}
			
			} else {
			
				if(response.toJSON().characteristicShortName == 'complete') {
					window.location.hash = "#edit/complete/question/" + response.toJSON().questionId;
				} else {
					window.location.hash = "#edit/characteristic/"+ response.toJSON().characteristicId +"/question/" + response.toJSON().questionId;
				}
			}
			
		},
		error: function(response){ 
			alert('There was an error contacting the server and the next characteristic could not be loaded. Please check your connection and try again.');
			$('.editCodingLoading').hide();
		}
	});	
};
