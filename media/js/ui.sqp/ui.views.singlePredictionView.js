	/// View for a single question row item in the question list
	sqpBackbone.views.singlePredictionView = Backbone.View.extend({
		
		initialize: function() { this.render();},
		tagName: 'div',
		render: function(){ 
			// render output with ICanHaz.js template
			$(this.el).html(ich.singlePredictionItem(this.model.toJSON()));
			var predictions = this.model.get('paramaterViews');
			for (var i = 0; i < predictions.length; i ++) {
				this.loadPrediction(predictions[i]['predictionId']);
			}
			return this;
		},
		loadPrediction : function (predictionId) {
			var view = this;
			$.ajax({
						url: '/sqp/api/renderPrediction/?questionId=' 
						     + view.model.get('questionId') 
							 + '&predictionId=' 
							 + predictionId,
						success: function(data){
							view.$('.prediction_' + predictionId).html('');
							view.$('.prediction_' + predictionId).html($.trim(data));
						},
						dataType : 'html'
					}
				 )
		}
	});