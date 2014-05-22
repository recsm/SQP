sqpBackbone.collections.studyListFitted = Backbone.Collection.extend({
	url: '/sqp/api/studyListFitted/',
	model: sqpBackbone.models.studyItem,
	parse: function(response){
		return sqpBackbone.helpers.responseHandler(response);
	}
});