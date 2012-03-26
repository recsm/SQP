



sqpBackbone.helpers.getTextSnippet = function getTextSnippet(fromString, maxLength){	
	
	var htmlStripped =  fromString.replace(/(<([^>]+)>)/ig,"")
	
	if(htmlStripped.length > maxLength) {
		 var space = htmlStripped.indexOf(" ", maxLength);
		 htmlStripped = htmlStripped.substr(0, space) + '...';
	}
	
	return htmlStripped;
};