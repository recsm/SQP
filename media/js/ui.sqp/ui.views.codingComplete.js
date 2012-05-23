

	// **NEW
	// Coding Complete View
	sqpBackbone.views.codingCompleteView = Backbone.View.extend({
		initialize: function() { 
			this.render();
		},
		render: function(){ 
			$(this.el).html(ich.codingCompleteTemplate({}));
			//console.log(this.model.toJSON());
			
			$('#continueCoding').hide();
					
			this.$('.btn').button();
			this.$('.returnToList').click(function() {
				if(sqpBackbone.app.isWorkingOnAssignment) {
					window.location.hash = '#assignedQuestionsList';
				} else {
					//Call the main controller to open the current question list
					sqpBackbone.app.openQuestionList();
				}
			});
			
			this.$('.getQualityPrediction').click(function() {
				//Switch to the prediction screen for the current question
				window.location.hash = '#questionPrediction/' + sqpBackbone.app.currentQuestion.get('id');
			});
			
			var view = this;
			if(sqpBackbone.app.isWorkingOnAssignment) {
				
				var assignedQuestions = new sqpBackbone.collections.assignedQuestionsList();
				
				assignedQuestions.fetch({
					success: function() {
						var nextQuestionFound = false;
						assignedQuestions.each(function (assignedQuestion) {
							if((assignedQuestion.get('completeness') != 'completely-coded') && !nextQuestionFound) {
								nextQuestionFound = true;
								view.$('.codeNextNotice').show();
								view.$('.codeNextInfo').html(assignedQuestion.getTitle());
								view.$('.codeNextQuestion').click(function() {
									window.location.hash= assignedQuestion.getCodingHref();
								})
								view.$('.codeNextLoading').hide();
							}
						});
					}
				});
				
			} else {
				view.$('.codeNextLoading').hide();
			}
			return this;
		}
	});