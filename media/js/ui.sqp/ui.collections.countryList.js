sqpBackbone.collections.countryList = Backbone.Collection.extend({
	url: '/sqp/api/countryList/',		
	model: sqpBackbone.models.countryItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});