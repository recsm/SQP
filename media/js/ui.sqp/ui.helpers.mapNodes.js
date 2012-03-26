

//Tke the nodes property of an object and map the the properties to dom nodes
sqpBackbone.helpers.mapNodes = function sqpBackbone$mapNodes(view) {
	for(prop in view.nodes) {
		view.nodes[prop] = view.$('.' + prop);
		
		//Make sure we matched a node
		if(view.nodes[prop].length == 0) {
			alert('In mapNodes: prop ' + prop + ' could not be mapped to a node. Do you have a dom node in your template with the class ".' + prop + '"?');
		}		
	}
}