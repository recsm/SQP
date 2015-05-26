sqpBackbone.collections.countryPredictionList = Backbone.Collection.extend({
	url: '/sqp/api/countryPredictionList/',		
	model: sqpBackbone.models.countryItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});