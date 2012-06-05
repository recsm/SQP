	
	/// **NEW The Question List Table
	sqpBackbone.views.questionListView = Backbone.View.extend({
		//These all get converted into jQuery node selectors by class name in mapNodes
		nodes : {
			qListStudy			:null,
			qListCountry		:null,
			qListLanguage		:null,
		//	qListTypeAll		:null,
		//	qListTypeTodo		:null,  //To be added back into the view customized for the coder
		//	qListTypeComplete	:null,
			qListTypePredicted	:null,
			qListTypeMTMM		:null,
			qListTable			:null,
			qListFromRow		:null,
			qListToRow      	:null,
			qListTotal      	:null,
			qListNextPage	    :null,
			qListPrevPage	    :null,
			qListNoResults      :null,
			qListLoading        :null,
			qListResults        :null,
			qListBreadCrumb     :null,
			qListLoadingContent :null,
			qListSearch			:null,
			qListSearchText     :null
		},
		initialize: function() {
			var view = this;
			
			//Map our dom nodes to jQuery objects for this view
			sqpBackbone.helpers.mapNodes(this);
			
			this.nodes.qListNoResults.hide();
			this.renderStudySelect();
			this.renderCountrySelect();
			this.renderLanguageSelect();
			
		
			//Bind our study select
			sqpBackbone.shared.studies.bind('refresh', function() {
				view.renderStudySelect();
			});
			
			//Bind our country select
			sqpBackbone.shared.countries.bind('refresh', function() {
				view.renderCountrySelect();
			});
			
			//Bind our language select
			sqpBackbone.shared.languages.bind('refresh', function() {
				view.renderLanguageSelect();
			});
			
			//Bind our question list refesh
			this.collection.bind('refresh', function() {
				view.renderQuestionList();
			});
			
			//Bind our question list refesh
			this.collection.bind('loading', function() {
				view.showLoading();
			});
			
			//Bind our question list failed
			this.collection.bind('failed', function() {
				view.informFailed();
			});
			
			this.loadQuestions();
			
			//Init buttons
			this.nodes.qListNextPage.button({
	            icons: {
	                secondary: "ui-icon-circle-triangle-e"
					
	            },
				text:false
			});
			
			this.nodes.qListPrevPage.button({
	            icons: {
	                primary: "ui-icon-circle-triangle-w"
	            },
				text:false
			});
			
			this.nodes.qListSearch.button({
	            icons: {
	                primary: "ui-icon-search"
	            },
				text:false
			});
		},
		loadQuestions : function loadQuestions() {
			// Load the json data into our collection Object
			// for the initial view
			var view = this;
			this.showLoading();
			this.collection.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));},
				// Once the Model is loaded render the View
				success: function(msg){
					view.renderQuestionList();
				}
			});
		},
	  	events: {
			
			//Search selects
			"change .qListStudy"         : "updateSearch",
			"change .qListCountry"		: "updateSearch",
			"change .qListLanguage"		: "updateSearch",
			
			//These are the checkboxes options to show question types
//			"click .qListTypeAll"		: "showCompletenessAll",
//			"click .qListTypeTodo"		: "showCompletenessTodo",
			"click .qListTypePredicted"	: "updateCompleteness",
			"click .qListTypeMTMM"		: "updateMTMM",
			//Paging events
			"click .qListNextPage"		: "nextPage",
			"click .qListPrevPage"		: "prevPage",
			"click .closePreview"		: "clearPreviewId",
			"click .qListSearch"		: "updateSearch"
			
		},
		showLoading : function () {
			//Show the question loading
			this.nodes.qListLoading.show();
			this.nodes.qListLoading.width(this.nodes.qListResults.width());
			this.nodes.qListLoadingContent.height(this.nodes.qListTable.height());
			this.nodes.qListLoadingContent.fadeTo('fast', 0.5, function () {});
		},
		informFailed : function () {
			
			alert('Error contacting the server. Please check your internet connection and try again.');
			
			this.nodes.qListLoading.hide();

		},
		renderQuestionList: function(){
			
			this.nodes.qListLoading.hide();
			//this.hideQuestionPreview();
			if (this.collection.meta.totalRecords == 0) {
				this.nodes.qListNoResults.show();
				this.nodes.qListResults.hide();
			} else {
				
				this.nodes.qListNoResults.hide();
				
				
				var view = this;
				
				//Remove old rows
				$('td', this.nodes.qListTable).remove();
				
				//Add in new rows
				this.collection.each(function(question){
					var qView = new sqpBackbone.views.singleQuestionView({
						model: question,
						questionListView : view
					});
					view.nodes.qListTable.append(qView.el);
				});
				
				this.nodes.qListTotal.html(this.collection.meta.totalRecords);
				this.nodes.qListFromRow.html((this.collection.meta.currentPage - 1) * this.collection.meta.recordsPerPage + 1);
				
				var toRow = (this.collection.meta.currentPage) * this.collection.meta.recordsPerPage;
				if (toRow > this.collection.meta.totalRecords) {
					toRow = this.collection.meta.totalRecords;
				}
				
				this.nodes.qListToRow.html(toRow);
				
				var nextState = this.collection.meta.nextPage ? 'enable' : 'disable';
				var prevState = this.collection.meta.prevPage ? 'enable' : 'disable'
				
				this.nodes.qListNextPage.button(nextState);
				this.nodes.qListPrevPage.button(prevState);
				
				this.nodes.qListResults.show();
				
				
			}
			
			//Set all of the selects correctly to the values in the collection
			this.nodes.qListStudy.val(this.collection.study);
			this.nodes.qListLanguage.val(this.collection.language);
			this.nodes.qListCountry.val(this.collection.country);
			
			/* Trigger the change event so the comboboxes can receive it and update the text*/
			this.nodes.qListStudy.trigger('change');
			this.nodes.qListLanguage.trigger('change');
			this.nodes.qListCountry.trigger('change');
			
			var completeText = '';
			
			/*
			if (this.collection.completeness == 1) {
				//Complete
				this.nodes.qListTypeComplete.attr('checked', 'checked' );
				completeText=" Coded "
			} else {
				this.nodes.qListTypeComplete.attr('checked',false );
			}
			
			*/
			
			if (this.collection.completeness == 3) {
				//Complete
				this.nodes.qListTypePredicted.attr('checked', 'checked' );
				completeText=" Coded "
			} else {
				this.nodes.qListTypePredicted.attr('checked',false );
			}
			
			if (this.collection.MTMM == 1) {
			   	//MTMM
				this.nodes.qListTypeMTMM.attr('checked', 'checked' );
				completeText += " MTMM "
			} else {
				//All questions
				this.nodes.qListTypeMTMM.attr('checked', false );
			}
			
			var countryStudyLangText = [];
			//Work a bit more on the breadcrumb text
			if(this.nodes.qListStudy.val() && this.nodes.qListStudy.val() != 'all') {
				countryStudyLangText.push(this.$(".qListStudy option[value='" + this.nodes.qListStudy.val() + "']").text());
			}
			
			if(this.nodes.qListCountry.val() && this.nodes.qListCountry.val() != 'all') {
				countryStudyLangText.push(this.$(".qListCountry option[value='" + this.nodes.qListCountry.val() + "']").text());
			}
			
			if(this.nodes.qListLanguage.val() && this.nodes.qListLanguage.val() != 'all') {
				countryStudyLangText.push(this.$(".qListLanguage option[value='" + this.nodes.qListLanguage.val() + "']").text());
			}
			
			if(countryStudyLangText.length > 0) {
				countryStudyLangText = '(' + countryStudyLangText.join(', ') + ')';
			}  else {
				countryStudyLangText = '';
			}
			

			//Change the url of the question list bread crumb
			$('.openQuestionList').attr('href', '#questionList/' + this.collection.getURI());
			
			
			if( completeText  == '') {
				completeText = 'All Questions'
			} else {
				completeText += ' Questions'
			}
			//Change the text of the question list bread crumb
			$('.questionListTitle').html(completeText + ' ' + countryStudyLangText);
			
			return this;
	  	},
	  	currentRequestedPreviewId : 0,
	  	previewShowing : false,
	  	setQuestionPreview : function (id) {
	  		this.currentRequestedPreviewId = id;
	  		this.collection.setQuestion(this.currentRequestedPreviewId);
	  		this.updateWindowLocation();
	  	},
	  	showQuestionPreview : function () {
	  	
	  		var view = this;
	  	
	  		var showIt = function () {
	  			$('.qListPreview').animate({'right' : '0px'}, 300, function () {view.previewShowing = true;});

			  	// Get the full question overview
				var questionDetail = new sqpBackbone.models.questionItem();
				questionDetail.url = questionDetail.url + view.currentRequestedPreviewId;
			
				
				// load json into out question model
				questionDetail.fetch({
					success: function(msg){
					
						if(view.currentRequestedPreviewId != questionDetail.get('id')) return;
						
						$('.qListCurrentQuestionBreadCrumb.breadCrumbCurrent').html(questionDetail.getTitle());
						$('.qListCurrentQuestionBreadCrumb').show();
						
						questionDetail.set({showPrediction : false, showMTMM : true, isPreview : true});
						//console.log('rendering');
						// render the json array with our view object.
						var qDetail = new sqpBackbone.views.questionDetailView({
							el: $('#qListPreviewContent'),
							model: questionDetail
						});
			  		}, 
					error : function () {
						alert('There was an error reaching the server. Please check your internet connection and try again.');
						/* Go back to the page before which should be the already loaded question list */
					}
				});
			}
					
	  		if(this.previewShowing) {
	  			setTimeout(showIt, 200);
	  			this.hideQuestionPreview();
	  		} else {
	  			showIt();
	  		}
	  		
	  	},
	  	clearPreviewId : function () {
	  		this.collection.setQuestion(0);
	  		this.currentRequestedPreviewId = 0;
	  		this.hideQuestionPreview();
	  		this.updateWindowLocation();
	  		$('.selectedQuestionRow').removeClass('selectedQuestionRow');
	  	},
	  	hideQuestionPreview : function() {
	  		var view = this;
	 		$('.qListPreview').animate({'right' : '-800px'}, 200, function () {
	  			$('#qListPreviewContent').html('Loading Question Detail...');
	  		});
	  		view.previewShowing = false;
	  		
	  		$('.qListCurrentQuestionBreadCrumb').hide();
	  	},
		updateSearch: function updateSearch(){
			//We call all of these, since the collection is configured to 
			//only refresh when its url changes, only one change can be clicked
			//by the user at a time 
			//Also the question collection does change checking before
			//refreshing the page and url
			var studyVal   = this.nodes.qListStudy.val() == 'all' || !this.nodes.qListStudy.val() ? "" : this.nodes.qListStudy.val();
			var countryVal = this.nodes.qListCountry.val() == 'all' || !this.nodes.qListCountry.val() ? "" : this.nodes.qListCountry.val();
			var languageVal   = this.nodes.qListLanguage.val() == 'all' || !this.nodes.qListLanguage.val() ? "" : this.nodes.qListLanguage.val();
			
			this.collection.setStudy(studyVal);
			this.collection.setLanguage(languageVal);
			this.collection.setCountry(countryVal);
			this.collection.setSearchText(this.nodes.qListSearchText.val());
			this.clearPreviewId();
			this.updateWindowLocation();
			
		},
		updateWindowLocation : function updateWindowLocation() {
			window.location = '/loadui/#questionList/' + this.collection.getURI();
		},
		updateCompleteness : function updateCompleteness() {
			this.clearPreviewId();
			
			if (this.nodes.qListTypePredicted.attr('checked') == 'checked') {
				//0 = All
				//1 = Complete by me
				//2 = Incomplete by me
				//3 = With a prediction by any user
				this.collection.setCompleteness(3);
			} else {
				this.collection.setCompleteness(0);
			}
			
			this.updateWindowLocation();
		},
		updateMTMM : function updateMTMM() {
			this.clearPreviewId();
			
			if (this.nodes.qListTypeMTMM.attr('checked') == 'checked') {
				this.collection.setMTMM(1);
			} else {
				this.collection.setMTMM(0);
			}
			
			this.updateWindowLocation();
		},
		nextPage : function nextPage(event) {
			event.preventDefault();
			if(this.collection.meta.nextPage) {
				this.clearPreviewId();
				this.collection.nextPage();
				this.updateWindowLocation();
			}
		},
		prevPage : function prevPage(event) {
			event.preventDefault();
			if(this.collection.meta.prevPage) {
				this.clearPreviewId();
				this.collection.prevPage();
				this.updateWindowLocation();
			}
		},
		renderStudySelect : function renderStudySelect() {
			var view = this;
			this.nodes.qListStudy.children().remove();
			this.nodes.qListStudy.append('<option value="all">All Studies</option>');
			//Add in options
			sqpBackbone.shared.studies.each(function(study) {
				 view.nodes.qListStudy.append('<option value="' + study.get('id') + '">' + study.get('name') + '</option>');	
				 
			});
			this.nodes.qListStudy.combobox();
			
		},
		renderCountrySelect : function renderCountrySelect() {
			var view = this;
			this.nodes.qListCountry.children().remove();
			this.nodes.qListCountry.append('<option value="all">All Countries</option>');
			//Add in options
			sqpBackbone.shared.countries.each(function(country) {
				 view.nodes.qListCountry.append('<option value="' + country.get('iso') + '">' + country.get('name') + '</option>');	
			});
			this.nodes.qListCountry.combobox();
		},
		renderLanguageSelect : function renderLanguageSelect() {
			var view = this;
			this.nodes.qListLanguage.children().remove();
			this.nodes.qListLanguage.append('<option value="all">All Languages</option>');
			//Add in options
			sqpBackbone.shared.languages.each(function(language) {
				 view.nodes.qListLanguage.append('<option value="' + language.get('iso') + '">' + language.get('name') + '</option>');	
			});
			this.nodes.qListLanguage.combobox();
		}
  	});