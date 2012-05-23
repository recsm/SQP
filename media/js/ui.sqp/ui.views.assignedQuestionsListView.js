	
	///  The Study List Table
	sqpBackbone.views.assignedQuestionsListView = Backbone.View.extend({
		initialize: function() {
			this.render();
		},
		render: function(){
		
			var view = this;
			$(view.el).html('');
				view.collection.each(function(assignedQuestion){
				var qView = new sqpBackbone.views.assignedQuestionRowView({
					model: assignedQuestion
				});
				console.log(view.el);
				$(view.el).append(qView.el);
			});
			return this;
	  	}
  	});