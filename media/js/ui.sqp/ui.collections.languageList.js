sqpBackbone.collections.languageList = Backbone.Collection.extend({
	url: '/sqp/api/languageList/',		
	model: sqpBackbone.models.languageItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});