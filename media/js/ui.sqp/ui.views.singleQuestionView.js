
	/// View for a single question row item in the question list
	sqpBackbone.views.singleQuestionView = Backbone.View.extend({
		questionListView : false,
		initialize: function() { 
			this.questionListView = this.options.questionListView;
			this.render();
			$(this.el).css('cursor' , 'pointer');
		},
		events : {
			'click' : 'handleItemClick',
			'mouseover' : 'handleOver',
			'mouseout' : 'handleOut'
		},
		handleItemClick : function (event) {
			event.preventDefault();
			//For researcher mode
			this.questionListView.setQuestionPreview(this.model.get('id'));
			//For coder mode we go directly to coding
			//TODO
			
			$('.selectedQuestionRow').removeClass('selectedQuestionRow');
			$(this.el).addClass('selectedQuestionRow');
			
			
		},
		handleOver : function () {
			$('.overQuestionRow').removeClass('overQuestionRow');
			$(this.el).addClass('overQuestionRow');
		},
		handleOut : function () {
			$(this.el).removeClass('overQuestionRow');
		},
		tagName: 'tr',
		render: function(){ 
			// render output with ICanHaz.js template
			var otherCountryPrediction=this.model.get('countryIso')!=this.model.get('countryPredictionIso');
			this.model.set({'otherPredictionCountry' : otherCountryPrediction});
			$(this.el).html(ich.singleQuestionListItem(this.model.toJSON()));
			
			return this;
		}
	});