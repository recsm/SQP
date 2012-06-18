	
	// **New Question Detail view
	sqpBackbone.views.questionImprovementView = Backbone.View.extend({
		completionId : 0,
		questionQuality : 0,
		initialize: function() { 
			var view = this;
			
			if (this.options.completionId) {
				this.completionId = this.options.completionId;
			}
			
			this.questionQuality = this.options.qualityInfo.question_quality;
			
			this.onImprovementsLoaded = this.options.onImprovementsLoaded;
			this.potentialImprovements = new Backbone.Collection;
			
			/* This will handle the sorting automatically*/
			this.potentialImprovements.comparator = function (improvementModel) {
				return (-1 * improvementModel.get('qualMax'));
			};
		  
			$('.questionImprovementLoadingCount').html('');
			$('.questionImprovementCurrentlyLoading').html('Loading variables');
			$('#questionImprovementLoading').show();
			$('#questionImprovementContainer').show();
			$('.qImprovementSelected').html('');
			$('.qImprovementList').html('<tr></tr>');
			$('.qImprovementList').height(0);
			$('.qImprovementListLoadAllHolder').html('');
			
			
			
			
			this.getAllXNames(function (xNames) {
				
				/* Yeah for underscore.js without method! */
				view.improvementLists['all']['variables']  = _.without(xNames, view.removeVars);
				 /* Make sure our list of top variables does not contain xNames that are not applicable 
			        Yeah for underscore.js intersection method! */
			    view.improvementLists['top']['variables'] = _.intersection( view.improvementLists['top']['variables'], view.improvementLists['all']['variables']);
			    
				view.loadList(view.showImprovementList);
			});
			
			//This model references a question, same as the question detail view
			//Show the question on top
			this.qDetailView = new sqpBackbone.views.questionDetailView({
				el: this.$('#qImprovementQuestionDetail'),
				model: this.model,
				hideQuestionText : true
			});
		},
		showImprovementList : 'top',
		improvementLists : { 'top': {'variables' :       [  'ncategories',
															  'labels',
															  'scale_corres',
															  'range.correspondence',
															  'fixrefpoints',
															  'stimulus',
															  'interviewer',
															  'balance',
															  'labels_order',
															  'form_basic',
															  'position',
															  'gradation',
															  'showc_horiz',
															  'scale_basic',
															  'nsyll_total',
															  'avgwrd_total',
															  'scal_neutral',
															  'used_WH_word',
															  'visual',
															  'showc_start'
														],
										'title' : "Top Variables (over all questions)"},
							'all' : {'variables' : [],
									 'title' : "All Variables"}
							},
		removeVars : [   // A list of vars never to show in potential improvements since they are not useful
			'concept', 'domain', 'socdesir', 'country', 'language'
		],
		onImprovementsLoaded : false, /* This can be overridden by the options passed to the view */
		xNames : [],
		_nextXNameIndex : 0,
		lastLoadedXName : false,
		potentialImprovements: false,
		loadList : function(listName) {
			this._nextXNameIndex = 0;
			//Loads all of the variable names and then the loop function
		 	var view = this;
		 	this.showImprovementList = listName;
		 	$('.questionImprovementCurrentlyLoading').html('Loading ' + this.improvementLists[listName]['title'] + '...');
	 		if (!view.isLoading) {
				view.loadImprovements_whileNext();
				view.loadImprovements_whileNext();
			} 
			this.initImprovementModels();
	 		this.renderList();
		},
		getAllXNames : function (onLoaded) {
			var view = this;
			$.ajax({
						type: 'GET',
						url: '/sqp/api/getXNames/',
						success: function(data){
							var xNames = data;
							/* Call the onload callback we were passed*/
							onLoaded(xNames);
						},
						dataType : 'json'
					}
				 );
		},
		initImprovementModels : function () {
			var view = this;
			var currentList = this.improvementLists[this.showImprovementList]['variables'];
			_.each(currentList, function (xName) {
				view.getOrCreateImprovement(xName);
			});
		},
		getOrCreateImprovement : function(xName) {
			var model = false;
			this.potentialImprovements.each(function(impModel) {
				if (impModel.get('xName') == xName) {
					model = impModel;
				}
			});
			if (!model) {
				var model = new sqpBackbone.models.potentialImprovement({
			 		'cid'	 : xName, /* Client Id Property used by backbone.collection.getByCid() */
			 		'xName' : xName,
					'questionId' : this.model.get('id'),
					'loaded' : false,
					'isError' : false,
					'qualMax' : -1,
					'questionQuality' : this.questionQuality, 
					'completionId' : this.completionId 
					});
				 this.potentialImprovements.add(model);
			}
			return model;
		},
		loadImprovements_whileNext : function() {
			//Loops through all xNames, loads them, then renders the view - recursive
			this.isLoading = true;
			var view = this;
			var currentList = this.improvementLists[this.showImprovementList]['variables'];
			
			var xName = currentList[this._nextXNameIndex];
			this._nextXNameIndex += 1;
			if (!xName) {
				//Completed Loading
				$('.questionImprovementCurrentlyLoading').hide();
				this.showLinkToAllVars();
				this.isLoading = false;
				if (this.onImprovementsLoaded) {
					this.onImprovementsLoaded();
				}
				return;
			}
			
			
			$('.questionImprovementCurrentlyLoading').html("Calculating " + (this.getTotalLoaded() + 1) + "/" + currentList.length +  ": " +xName);
			$('.questionImprovementCurrentlyLoading').show();
			
			var found = false;
			/* Already loaded this improvement from a previous list, so we skip the ajax call */
			this.potentialImprovements.each(function(impModel) {
					if (impModel.get('xName') == xName && impModel.get('loaded')) found = true;
				});
				
			if (found) {
				 this.loadImprovements_whileNext();
				 return;
			}
			
			if (this.completionId) {
				var completionIdPart = '&completionId=' + this.completionId;
			} else {
				var completionIdPart = '';
			} 
			
			
			$.ajax({
						type: 'GET',
						url: '/sqp/api/getPotentialImprovements/?xname=' 
							  + xName 
							  + '&params=qual2,choiceOptions&questionId='
							  + view.model.get('id')
							  + completionIdPart,
						success: function(data){
							
							
							/* If the user changed views while the ajax callback was loading,
							   we are no longer on this screen so we stop the loading loop. */
							if ((sqpBackbone.app.currentView != 'questionImprovement') ||
							    (sqpBackbone.app.currentImprovementId != view.model.get('id'))) {
								return;
							}
							
							if(data['success']) {
								var model = view.getOrCreateImprovement(xName);
								model.set(data['payload']);
								model.set({'xName'   : xName,
										   'loaded'  : true
										  });
							} else {
								var model = view.getOrCreateImprovement(xName);
								model.set({
										   'isError' : true,
										   'loaded'  :true,
										   'cid'	 : xName, /* Client Id Property used by backbone.collection.getByCid() */
										   'errorMessage' : data['error_message'],
								 		   'qualMax' : -99
								 		    });
							}
							model.setDerivedProperties();
							
							
							view.lastLoadedXName = xName;
							view.renderList();
							view.loadImprovements_whileNext();
							
						},
						dataType : 'json'
					}
				 );
		},
		getTotalLoaded : function() {
			var loaded = 0;
			var currentList = this.improvementLists[this.showImprovementList]['variables'];
			this.potentialImprovements.each(function (improvementModel) {
				var xName = improvementModel.get('xName');
				if (_.indexOf(currentList, xName ) != '-1') {
					if (improvementModel.get('loaded')) {
						loaded += 1;
					}
				} 
			});
			return loaded;
		},
		linkToAllVarsShown : false,
		showLinkToAllVars : function() {
			if(this.linkToAllVarsShown == true) return;
			this.linkToAllVarsShown = true;
			var view=this;
			if(this.showImprovementList != 'all') {
			
				var intro = "<p>The top variables by effect in general have been evaluated. However for this specific question, other variables may also be important.</p>"
				var link  = $(intro + '<div class="buttonHolder" style="padding-bottom:10px;"><button class="btn qImprovementAllLink">Evaluate all remaining variables &gt;</button></div>');
				$('.qImprovementListLoadAllHolder').append(link);
				$('.qImprovementAllLink').click(function() {view.loadList('all');$('.qImprovementListLoadAllHolder').html('');view.renderListTitle();});
				this.$('.btn').button();
			}
		},
		showXName : function (xName) {
			var model = this.getOrCreateImprovement(xName)
			//Create an instance of the improvement detail view to show on the right
			var qImprovementDetailView = new sqpBackbone.views.questionImprovementDetailView({
				el: $('#qImprovementDetailContainer'),
				questionId : this.model.get('questionId'),
				xName : xName,
				model : model
			});
		},
		renderListTitle : function () {
				$('.qImprovementListHeader').html(this.improvementLists[this.showImprovementList]['title']);
			
		},
		renderList: function(){
			var view = this;
			
			this.potentialImprovements.sort();
			/* Fix the height to avoid auto scrolling */
			
			$('.qImprovementListHolder').height($('.qImprovementListHolder').height());
			$('.qImprovementList').html('');
			var currentList = this.improvementLists[this.showImprovementList]['variables'];
			this.renderListTitle();
			
			this.potentialImprovements.each(function (improvementModel) {
				/*If the xName of the model is not in our current list then we skip it
				  Uses the underscore library directly underscore.js */
				if (_.indexOf(currentList, improvementModel.get('xName')) != -1) {
					var improvementView = new sqpBackbone.views.singlePotentialImprovement({
					    model : improvementModel
					});
					
					view.$('.qImprovementList').append(improvementView.el);
					
					
					if(improvementModel.get('xName') == view.lastLoadedXName) {
						improvementView.flash();
					}
				}
					
			});
			
			$('.qImprovementListHolder').css('height', 'auto');
			return this;	
	  	}
  	});