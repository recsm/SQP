
	
	// **New Question Detail view
	sqpBackbone.views.questionDetailView = Backbone.View.extend({
		initialize: function() { 
			this.render();
		},
		events : {
			'click .viewMTMM' : 'showPreviewMTMM',
			'click .hideMTMM' : 'hidePreviewMTMM',
			'click .showQuestionText' : 'showQuestionText',
			'click .hideQuestionText' : 'hideQuestionText'
		},
		render: function(){
			var view = this;
		
		    this.model.set({'title': this.model.getTitle()});
			
			// render output with ICanHaz.js template
			$(this.el).html(ich.questionDetail(this.model.toJSON()));
			
			this.$('.btn').button();
			
			this.$('.buttonEditQuestion').click(function() {
				view.editQuestion();
			});
			
			this.$('.getQualityPrediction').click(function() {
				view.showPrediction();
			});
			
			if (this.model.get('isPreview')) {
				this.$('.MTMMInfoHolder').css({'left' : 800, 'position' : 'absolute'});
				this.$('.questionPreview').css({'left' : 10, 'position' : 'absolute'});
			}
			
			if (this.options.hideQuestionText) {
				this.$(".showQuestionTextLinkHolder").show();
				this.$(".questionText").hide();
			}
			
			
			
			return this;	
	  	},
	  	editQuestion : function () {
	  		window.location.hash = "#edit/question/" + this.model.get('id');
		},
		showPrediction : function () {
			window.location.hash = "#questionPrediction/" + this.model.get('id');
		},
		showPreviewMTMM : function () {
			var view = this;
			view.$('.questionText').hide();
			view.$('.questionPreview').animate({'left' : -800}, 350, function () { 
				
				view.$('.MTMMInfoHolder').animate({'left' : 10}, 200);
				
				});
		},
		hidePreviewMTMM : function () {
			var view = this;
			view.$('.MTMMInfoHolder').animate({'left' : 800}, 300, function () {
				view.$('.questionText').show();
				view.$('.questionPreview').animate({'left' : 10}, 200);		
			});
		},
		showQuestionText : function () {
			this.$(".showQuestionTextLinkHolder").hide();
			this.$(".questionText").slideDown();
			this.$(".hideQuestionTextLinkHolder").show();
		},
		hideQuestionText : function () {
			this.$(".hideQuestionTextLinkHolder").hide();
			this.$(".questionText").slideUp();
			this.$(".showQuestionTextLinkHolder").show();
		}
  	});