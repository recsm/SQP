	
	///  The Study List Table
	sqpBackbone.views.assignedQuestionsListView = Backbone.View.extend({
		initialize: function() {
			this.render();
		},
		render: function(){
		
			var view = this;
			$(view.el).html('');
			view.collection.each(function(assignedQuestion){
				/*
				var studyRowView = new sqpBackbone.views.studyRowView({
					model: study
				});
	
				view.nodes.studyListTable.append(studyRowView.el);
				*/
				$(view.el).append('<p><a href="' + assignedQuestion.getCodingHref() +'">' + assignedQuestion.getTitle() + ' / ' + assignedQuestion.toJSON().completeness + '</a></p>');
			});
			
			return this;
	  	}
  	});