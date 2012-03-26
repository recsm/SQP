sqpBackbone.collections.studyList = Backbone.Collection.extend({
	url: '/sqp/api/studyList/',		
	model: sqpBackbone.models.studyItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});