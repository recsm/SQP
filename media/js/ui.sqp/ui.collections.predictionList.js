sqpBackbone.collections.predictionList = Backbone.Collection.extend({
	url: '/sqp/api/predictionList/',		
	model: sqpBackbone.models.predictionItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});