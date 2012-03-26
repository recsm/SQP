sqpBackbone.collections.codingList = Backbone.Collection.extend({		
	model: sqpBackbone.models.codingListItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});