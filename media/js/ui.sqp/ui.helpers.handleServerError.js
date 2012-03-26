


//Handle an error codes returned by the server
sqpBackbone.helpers.handleServerError = function sqpBackbone$handleError(response){	
	if (response.error_key == 'server_error') {
		alert('There was an unexpected error on the server. Here are some details: \n\n ' + response.error_message)
	} else if (response.error_key == 'login_required') {
		alert('It seems you have been logged out. Please login and try again');
	} else if (response.error_key == 'object_not_found') {
		alert('Object not found. The object you were looking for cannot be found on the server.');
	} else if (response.error_key == 'bad_request') {
		alert('The request sent to the server was not valid. Here are some details: \n\n ' + response.error_message);
	} else if (response.error_key) {
		alert(response.error_key + ' ' + response.error_message)
	} else {
		alert('strange server response: ' + response)
	}
};