sqpBackbone.collections.assignedQuestionsList = Backbone.Collection.extend({
	url: '/sqp/api/getAssignedQuestions/',		
	model: sqpBackbone.models.questionItem,
	parse: function(response){		
		return sqpBackbone.helpers.responseHandler(response);
	}
});
