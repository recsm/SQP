sqpBackbone.helpers.responseHandler = function sqpBackbone$responseHandler(jsonResponse){
	if (jsonResponse.success == "1"){
		return jsonResponse.payload;
	} else {
		sqpBackbone.helpers.handleServerError(jsonResponse);
	}	
}