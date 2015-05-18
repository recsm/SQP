
	
	// **New Question Detail view
	sqpBackbone.views.questionPredictionView = Backbone.View.extend({
		completionId : 0,
		initialize: function() { 
		
			if (this.options.completionId) {
				this.completionId = this.options.completionId;
			}
			
			this.model.set({'predictionTitle' : this.model.getPredictedByInfo(this.options.completionId)});
			
			this.render();
		},
		nodes : {
			qualityCoefficients:	null,
			qualityPredictions: null
		},
		events : {
		    'click .showCoefficients' : 'showCoefficients',
		    'click .showQuality' : 'showQuality',
		    'click .getPredictionCodes' : 'showCodes',
		    'click .getQuestionImprovement' : 'showImprovement'
		    
		},
		linksDisabled : false,
		qDetailView : false,
		predictionListView : false,
		coefficientsLoaded : false,
		showQuality : function () {
		    if (this.linksDisabled) return;
			this.disableToggleLinks();
			this.nodes.qualityCoefficients.hide();
			this.nodes.qualityPredictions.fadeIn(); 
			
			
		},
		showCoefficients : function () {
			if (this.linksDisabled) return;
  			this.disableToggleLinks();
			if (! this.cofficientsLoaded) {
				this.loadPredictions('qualityCoefficients');
				this.coefficientsLoaded = true;
			}
						
			this.nodes.qualityPredictions.hide();
			this.nodes.qualityCoefficients.fadeIn(); 
			
		},
		disableToggleLinks : function() {
			//Disable the toggle links for a second, so they don't get clicked faster than the browser switches the mouse action
			//otherwise it is possible to see both the overview and coefficients at the same time
			var view = this;
			this.linksDisabled = true;
			this.$('.toggleLink').css('cursor', 'wait');
			setTimeout(function() {
				view.linksDisabled = false;
				view.$('.toggleLink').css('cursor', 'pointer');
			}, 700);
		},
		loadPredictions : function (group) {
		
			var view = this;
		  
		    var predictionKeyList = [];
		
			this.$('.' + group + ' .prediction').each(function(index){
			    var predictionNode = this;
				var predictionKey = $(predictionNode).attr('predictionKey');
				predictionKeyList.push(predictionKey);
			});
			
			$.ajax({
					url: '/sqp/api/renderPredictions/?questionId=' 
					     + view.model.get('id') 
					     + '&completionId='
					     + view.completionId 
						 + '&predictionKeyList=' 
						 + predictionKeyList.join(','),
					success: function(data){
					 	
					 	if (!data['success']) {
					 		view.$('.loadingPredictionsErrorInfo').html(data['meta']['general_error']);
					 		view.$('.loadingPredictions').hide();
					 		view.$('.loadingPredictionsError').show();
					 		
					 	} else {
					 		view.$('.' + group).show();
					 		view.$('.loadingPredictions').hide();
					 		view.$('.potentialImprovements').show();
					 		
					 		var payload = data['payload']
							view.$('.' + group + ' .prediction').each(function(index){
							    var predictionNode = this;
							    var predictionKey = $(predictionNode).attr('predictionKey');
								$(predictionNode).html($.trim(payload[predictionKey]));							
							});
					 	}
					},
					dataType : 'json'
				}
			 );
		},
		render: function(){
			var view = this;
			
			this.qDetailView = new sqpBackbone.views.questionDetailView({
				el: this.$('.qPredictionQuestionDetail'),
				model: this.model,
				hideQuestionText : true
			});
			
			
		
			// render output with ICanHaz.js template for the lists
			this.$('.qPredictionList').html(ich.predictionList(this.model.toJSON()));
			if(this.model.get('studyId')==88){ //special case ESS round 6
				this.$('.showCI').hide();
			}
			this.$('.qPredictionCodingList').html(ich.predictionCodingList());
			this.$('.loadingPredictionsError').hide();
			
			this.$('.potentialImprovements').hide();
			//Get the predictions required for the default view
			
			//Map our dom nodes to jQuery objects for this view
			sqpBackbone.helpers.mapNodes(this);
			this.nodes.qualityPredictions.hide();
			this.nodes.qualityCoefficients.hide();
			
			this.loadPredictions('qualityPredictions');
		
			this.$('.btn').button();
			
			return this;	
	  	}, 
	  	showImprovement : function () {
	  		window.location.hash = this.model.getImprovementHref(this.completionId);
	  	},
	  	showCodes : function () {
	  		window.location.hash = this.model.getCodingHref(this.completionId);
	  	}	  	
  	});