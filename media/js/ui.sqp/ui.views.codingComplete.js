

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
				//Call the main controller to open the current question list
				sqpBackbone.app.openQuestionList();
			});
			
			this.$('.getQualityPrediction').click(function() {
				//Switch to the prediction screen for the current question
				window.location.hash = '#questionPrediction/' + sqpBackbone.app.currentQuestion.get('id');
			});
			
			var view = this;
			//Load the next question id and info so we can link directly to it
			sqpBackbone.app.getNextQuestion(function(question) {
				if(question.get('id')) {
					view.$('.codeNextNotice').show();
					view.$('.codeNextInfo').html(question.getTitle());
					view.$('.codeNextQuestion').click(function() {
						window.location.hash='#question/' + question.get('id');
					})
					view.$('.codeNextLoading').hide();
				} else {
					view.$('.codeNextLoading').hide();
				}
			});
			
			return this;
		}
	});