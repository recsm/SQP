/////////////////
/// CONTOLLER ///
/////////////////

sqpBackbone.sqpWorkspace = Backbone.Controller.extend({
	
	initialize: function(option){

        // Load fitted studies. Doesn't allow insertions of questions in ESS and OldStudies
        sqpBackbone.shared.studiesfitted = new sqpBackbone.collections.studyListFitted;
		sqpBackbone.shared.studiesfitted.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));}
			});

		// Load our studies
		sqpBackbone.shared.studies = new sqpBackbone.collections.studyList;
		sqpBackbone.shared.studies.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));}
			});
			
			
		// Load our countries
		sqpBackbone.shared.countries = new sqpBackbone.collections.countryList;
		sqpBackbone.shared.countries.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));}
			});
		
		// Load prediction available countries 
		sqpBackbone.shared.predictionCountries = new sqpBackbone.collections.countryPredictionList;
		sqpBackbone.shared.predictionCountries.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));}
			});
			
		// Load our languages
		sqpBackbone.shared.languages = new sqpBackbone.collections.languageList;
		sqpBackbone.shared.languages.fetch({
				error: function(err){ alert("error: " + JSON.stringify(err));}
			});
			
		//Run some global jQuery functions
		//Maybe a global view would be good for this??
		$('.btn').button();
		
		//This is global since there is only one dom node 
		//during the run of the app. Would be ideal to refactor this
		//into the individual view for the question list at some point
		//as this really should not be global functionality
		
		var _controller = this;
		$('.nextCharacteristicButton').click(function(){
				var questionId = _controller.currentQuestion.get('id');
				//We make a call to the api (using jquery) to find the next id to code
				//and then redirect the browser to that url
				$.ajax({
						url: '/sqp/api/coding/?questionId=' + questionId,
						success: function(data){
							var characteristicId = data.payload.characteristicId;
							// change hash directly to trigger the route
							window.location.hash = "#edit/characteristic/" + characteristicId + "/question/" + questionId;
						},
						dataType : 'json'
					}
				 )
			});
		
		//On click outside the char full description  
		$('body, html').click(function() {
			$('.characteristicDescFull, .characteristicDescFullShadow').css('visibility', 'hidden');
		});
		$('#removeAssigment').click(function() {
			$('#assignmentNotice').hide();
			var assignedQuestions = new sqpBackbone.collections.assignedQuestionsList();
			assignedQuestions.fetch({
				success: function() {
					assignedQuestions.each(function(question){
						$.ajax({
							url: '/sqp/api/assignedQuestion/?assignedQuestionId='+ question.get("id") ,
							type:'delete',
							success: function(){
								// change hash directly to trigger the route
								window.location.hash = "#home";
							},
						})
					})
				},
				error : function() {
					alert('There was an error contacting the server.');
				}
	         });
			
		});
	},
	routes: {
		"": 												 "home", //default
		"home":												 "home",
		"assignedQuestionsList": 							"assignedQuestionsList", //list of all questions
		"questionList": 									 "questionList", //list of all questions
		"questionList/:query": 								 "questionList", //filtered list of questions
		"questionPrediction/:query/:query": 				 "questionPrediction", //prediction for a question by another user
		"questionPrediction/:query": 						 "questionPrediction", //prediction for a question
		"questionImprovement/:query/:query/variable/:query": "questionImprovementDetail", //improvement for one variable for a question based on other user's codings
		"questionImprovement/:query/variable/:query": 		 "myQuestionImprovementDetail", //improvement for one variable for a question based on user's own codings
		"questionImprovement/:query/:query": 				 "questionImprovement", //improvement for a question based on another user's 'codings
		"questionImprovement/:query": 						 "myQuestionImprovement", //improvement for a question based on user's own'codings
		"questionCoding/:query/:query":	 					 "questionCoding",  // #question/1/23423 question id/ completion id
		"questionCoding/:query":							 "questionCoding",  // #question/1
		"question/new":									     "newQuestion",  // #question/new
		"help":												 "help",		// #help
		"about": 											 "about", // #about
        "faq":                                               "faq", // #faq
		"settings":											 "settings",	
		"studies":											 "studies",
		"search":											 "search",
		"edit/question/:query":								 "editQuestion",
		"edit/characteristic/:query/question/:query":		 "editCharacteristic",
		"edit/complete/question/:query":					 "editCodingComplete",
		"characteristic/:query/question/:query/:query":		 "viewCharacteristic" //View characteristics from someone elses coding

	},
	currentCharacteristicId : false, //Which characteristic we are coding if any
	currentQuestion : false, /* Keep track of the current question we are editing 
	                            since a lot of sub views depend on the question 
	                            being loaded already */
	currentImprovementId : false, /* Like above, but just an id for the improvement screen*/
	questionListRendered : false, /* Keep track if the question list is rendered */
	questionListView : false, /* A reference to the question list view */
	questionListCollection : false, /* A reference to the question list collection */
	isWorkingOnAssignment : false, /* Did the user come from the question list view or the assigned question view when coding a question? */ 
	qImprovementView : false, /* A reference to the current potential improvement view */
	currentView : false, /* Keep track of what view we are currently showing */
	markCurrentRow : function () {
			//Mark the current characteristic on the table on the right side
			$('.characteristicRow_current').removeClass('characteristicRow_current');
			$('.characteristicRow_' + this.currentCharacteristicId).addClass('characteristicRow_current');
		},
	/* Determine the link to direct the browser back to our current question list
	 * and open it
	 */
	openQuestionList : function () {
		if(this.questionListCollection) {
			window.location.hash = '#questionList/' + this.questionListCollection.getURI();
			
		} else {
			window.location.hash = '#questionList';
		}
	},
	/*
	 * Clear any cached questions so when a question is edited
	 * the detail view and question list should be forced to refresh
	 */
	clearCachedQuestion : function () {
		this.currentQuestion = false;
		this.currentCharacteristicId = false;
	},
	assignedQuestionsList : function () {
		this.isWorkingOnAssignment = true;
		if (this.currentView != 'assignedQuestionsList') {
			sqpBackbone.helpers.hideAllPages();
			$("#pageAssignedQuestionList").fadeIn();
			$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
			this.currentView = 'assigne(dQuestionsList';
			$('.openQuestionList').html('My Assigned Questions').attr('href', '#assignedQuestionsList');
		}	
		
		var assignedQuestions = new sqpBackbone.collections.assignedQuestionsList();

		assignedQuestions.fetch({
			success: function() {
				
				sqpBackbone.helpers.updateAssignedCount(assignedQuestions);
				var assignedQuestionsListView = new sqpBackbone.views.assignedQuestionsListView({
					el: $('#assignedQListTable'),
					collection: assignedQuestions
				});
			},
			error : function() {
				alert('There was an error contacting the server.');
			}
         });
		
	},
	questionList: function(query){
		
		 this.isWorkingOnAssignment = false;
		 
		 if(query){
			 var queryDict = {}
			 var params = query.split('|');
			 for (var i in params) {
			 	var parts = params[i].split(':');
			 	queryDict[parts[0]] = parts[1]
			 }
		 } else {
		 	queryDict = {}
		 }
		 
		if (this.currentView != 'questionList') {
			// Show hide tabs for question list / detail
			sqpBackbone.helpers.hideAllPages();
			$("#pageQuestionList").fadeIn();
			$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
			$('.openQuestionList').html('Questions').attr('href', '#questionList');
			this.currentView = 'questionList'
		}		
		
		if (!this.questionListRendered) {
			
			//Since this is a global question list, we just render it once
			this.questionListRendered = true;
			
			// Create an instances of our question list model object
			this.questionListCollection = new sqpBackbone.collections.questionList;
			if(queryDict != {}) {
				
				this.questionListCollection.setFromDict(queryDict);

			}
			
			
			this.questionListView = new sqpBackbone.views.questionListView({
				el: $('#pageQuestionList'),
				collection: this.questionListCollection
			});
			
			this.questionListView.setQuestionPreview(this.questionListCollection.question);
			
		} else {
			
			this.questionListCollection.setFromDict(queryDict);
		}
	
		if(this.questionListCollection.question == 0) {
			this.questionListView.clearPreviewId();
		} else  {
			
			this.questionListView.showQuestionPreview();
		}
	},
	questionCoding: function(questionId, completionId, onLoad){
		
		var controller = this;
		
		if (this.currentView != 'question') {
			sqpBackbone.helpers.hideAllPages();
			$("#pageQuestionDetail").fadeIn();
			$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
			this.currentView = 'question'
		}
		
		//Do some showing and hiding of nodes
		$("#qDetailBreadCrumb").html('Loading..');
		$('#questionDetailContainer').html('');
		$('#questionDetailContainer').hide();
		$('#editCodingContainer').hide();
		$('.editCodingLoading').hide();
		$('#charateristicDetailContainer').hide()
		$('#qDetailContent').fadeIn();
		
		//Show the loading div
		$('#questionContainerLoading').fadeIn();
		
		// Create an instance of our question model object
		var questionDetail = new sqpBackbone.models.questionItem;
		questionDetail.url = questionDetail.url + questionId;
		
		if(completionId) {
			questionDetail.url  += '&completionId=' + completionId;
		} else {
			questionDetail.url  += '&prepSuggestions=True';
		}
		
		this.currentCharacteristicId = false;
		
		// load json into out question model
		questionDetail.fetch({
			success: function(msg){
				
				//Clear out other div ids that could contain information left
				//over from coding a previous question
				
				$('#editCodingContainer').html('');
				
				controller.currentQuestion = questionDetail;
			    
			    if (questionDetail.get('completeness') == 'completely-coded') {
			    	questionDetail.set({'showPredictionIntro': true});
			    }
			    
			    questionDetail.set({'showMTMM' : false});
			    
				// render the json array with our view object.
				var qDetail = new sqpBackbone.views.questionDetailView({
					el: $('#questionDetailContainer'),
					model: questionDetail,
					completionId : completionId
				});
				
				$("#qDetailBreadCrumb").html(questionDetail.getCodedByInfo(completionId));
				controller.updateQuestionBreadCrumb(questionDetail);
				
				
				if (questionDetail.toJSON().completeness == 'completely-coded' || questionDetail.toJSON().completeness == "partially-coded") {
					//alert("load coding detail data" + questionDetail.toJSON().completeness);
					$('#codingList').fadeIn();
					$('#codingListWelcome').hide();
					
					// load coding list
					var allCodings = new sqpBackbone.collections.codingList;
					allCodings.url = '/sqp/api/questionCodingHistory/?questionId='+questionId ;
					
					if(completionId) {
						allCodings.url += '&completionId=' + completionId;
					} 
					
					if(questionDetail.toJSON().completeness == "completely-coded") {
						$('#continueCoding').hide();
						
					} else {
						$('.nextCharacteristicButton').attr("href", "#edit/next/characteristic/question/" + questionId);
						$('#continueCoding').fadeIn();
					}
					
					allCodings.fetch({
							error: function(err){ alert("error: " + JSON.stringify(err));},
							success: function(msg){
								hList = new sqpBackbone.views.codingListView({
									collection: allCodings,
									completionId : completionId
								});
							}
					});

				} else {
								
					$('#codingList').hide();
					$('.nextCharacteristicButton').show();
					$('#codingListWelcome').fadeIn();
					
					$('.nextCharacteristicButton').attr("href", "#edit/next/characteristic/question/" + questionId);
					
				}
				
				/* if question() was passed an onLoad function as the second param, we call it */
				if(typeof(onLoad) == 'function') {
					onLoad();
				}
				
				$('#editCodingContainer').show();
				
				/* Show the content of the question div */
				$('#questionContainerLoading').hide();
				$('#charateristicDetailContainer').fadeIn()
				$('#questionDetailContainer').fadeIn();
				
			}, 
			error : function () {
				alert('There was an error reaching the server. Please check your internet connection and try again.');
				/* Go back to the page before which should be the already loaded question list */
			
			}
		});
	},
	verifyQuestionLoaded : function verifyQuestionLoaded(questionId, completionId, onLoad) {
		
		// Make sure that our parent question view is rendered
		// This functionality is useful to avoid recreating the entire page for every characteristic
		// being coded. It is needed in case some one uses the back button
		// or accesses a characteristic directly by the url
		
		if(!this.currentQuestion || 
		   (this.currentQuestion.get('id') != questionId) || 
		    this.currentView != 'question') {
			this.questionCoding(questionId, completionId, onLoad);
		
		} else {
			if(typeof(onLoad) == 'function') {
				onLoad();
			}
		}
	},
	
	editQuestion : function editQuestion(questionId){
		var controller = this;
		
		sqpBackbone.helpers.hideAllPages();
		$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
		$("#pageQuestionEdit").fadeIn();
		this.currentView = 'questionEdit';
		
		if(this.currentQuestion) {
			$("#qEditBreadCrumb").html(this.currentQuestion.getTitle());
			$("#qEditBreadCrumb").attr('href', '#question/' + this.currentQuestion.get('id'));

		} else {
			$("#qEditBreadCrumb").html('Loading...');
		}
		
		var questionDetail = new sqpBackbone.models.questionItem;
		questionDetail.url = questionDetail.url + questionId;
		
		// load json into out question model
		questionDetail.fetch({
			success: function(msg){
				// render the json array with our view object.
				var qEdit = new sqpBackbone.views.questionEditView({
					el: $('#questionEditContainer'),
					model: questionDetail
				});
			}, 
			error : function (msg) {
				alert('There was an error and the question could not be loaded.');
			} 
		});
	},
	newQuestion : function newQuestion(){
		sqpBackbone.helpers.hideAllPages();
		$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
		$("#pageQuestionNew").fadeIn();
		this.currentView = 'questionNew';
		
		var qNew = new sqpBackbone.views.questionEditView({
			el: $('#questionNewContainer'),
			model: new sqpBackbone.models.questionItem({'canEditDetails' : true,
			                                            'canEditText' : true,
                                                        'demoUser' : window.demouser})
		});
	},
	editCharacteristic: function(characteristicId, questionId){
		// Make sure that our parent question view is rendered
		this.verifyQuestionLoaded(questionId, false, function () {
			
			sqpBackbone.helpers.showCharacteristicWait();
			
			var characteristicCoding = new sqpBackbone.models.characteristicItem;
			characteristicCoding.url = "/sqp/api/coding/?questionId=" + questionId + "&characteristicId=" +characteristicId;
			characteristicCoding.fetch({
				success: function(msg){
					/*uncomment to simulate lag // setTimeout( function () { */
						var cCoding = new sqpBackbone.views.characteristicView({
						el: $('#editCodingContainer'),
						model: characteristicCoding,
						canEdit : true
					});
					/* uncomment to simulate lag // }, 2000); */
				},
				error: function(){
					alert('There was an error contacting the server and the characteristic could not be loaded. Please check your connection and try again.');
					$('.editCodingLoading').hide();
				}
			});
		});
	
	},
	viewCharacteristic: function(characteristicId, questionId, completionId){
	
		// Make sure that our parent question view is rendered
		this.verifyQuestionLoaded(questionId, completionId, function () {
			
			sqpBackbone.helpers.showCharacteristicWait();
			
			var characteristicCoding = new sqpBackbone.models.characteristicItem;
			characteristicCoding.url = "/sqp/api/coding/?questionId=" + questionId + "&characteristicId=" +characteristicId;
			
			if(completionId) {
				characteristicCoding.url += '&completionId=' + completionId;
			}
			
			characteristicCoding.fetch({
				success: function(msg){
						var cCoding = new sqpBackbone.views.characteristicView({
						el: $('#editCodingContainer'),
						model: characteristicCoding,
						canEdit : false,
						completionId : completionId
					});
				},
				error: function(){
					alert('There was an error contacting the server and the characteristic could not be loaded. Please check your connection and try again.');
					$('.editCodingLoading').hide();
				}
			});
		});
	},
	editCodingComplete:function(questionId){
		this.verifyQuestionLoaded(questionId, false, function() {
		
			$('.editCodingLoading').hide();
			//window.location.hash = "#edit/complete/question/" + questionId;
			var cCoding = new sqpBackbone.views.codingCompleteView({
						el: $('#editCodingContainer')
					});
			$('#editCodingContainer').fadeIn();
		});
	},
	updateQuestionBreadCrumb : function (questionModel) {
		
		$('.questionTitleBreadCrumb').html('Question ' + questionModel.getShortTitle());

		if (this.isWorkingOnAssignment) {
			$('.questionTitleBreadCrumb').removeAttr('href');
			$('.questionTitleBreadCrumb').css('color', '#555');

		} else {
			$('.questionTitleBreadCrumb').css('color', '#2452F5');

			if(!this.questionListView) {
				$('.questionTitleBreadCrumb').attr('href', '#questionList/question|' + questionModel.get('id'));
			} else {
				$('.questionTitleBreadCrumb').attr('href', '#questionList/' + this.questionListView.collection.getURI());
			}
		}
		
	},
	questionPrediction : function (questionId, completionId) {
		var controller = this;completionId
		
		if (this.currentView != 'questionPrediction') {
			sqpBackbone.helpers.hideAllPages();
			$("#pageQuestionPrediction").fadeIn();
			$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
			this.currentView = 'questionPrediction'
		}
		
		// Create an instance of our question model object
		var question= new sqpBackbone.models.questionItem();
		question.url = question.url + questionId + '&randForRefresh=' + Math.random();
		
		$("#qCodingBreadCrumb").html('Loading...');
		$("#breadCrumpPrediction").html('Quality Prediction');
		$("#questionPredictionContainer").hide();
		
		// load json into out question model
		question.fetch({
			success: function(msg){
				question.set({'showPrediction' : 0}); //We don't want to ever show the prediction summary on the prediction view, would be redundant
				
				// render the json array with our view object.
				var qPrediction = new sqpBackbone.views.questionPredictionView({
					el: $('#questionPredictionContainer'),
					completionId: completionId,
					model: question
				});
				
				controller.updateQuestionBreadCrumb(question);
				
				$("#qCodingBreadCrumb").html(question.getCodedByInfo(completionId));
				$("#breadCrumpPrediction").html(question.getPredictedByInfo(completionId));
				$("#qCodingBreadCrumb").attr('href',question.getCodingHref(completionId));
				$("#questionPredictionLoading").hide();
				$("#questionPredictionContainer").show();
				
			}, 
			error : function () {
				alert('There was an error reaching the server. Please check your internet connection and try again.');
				/* Go back to the page before which should be the already loaded question list */
			
			}
		});
	}, 
	myQuestionImprovement : function  (questionId, showXName) {
		return this.questionImprovement(questionId, 0, showXName);
	},
	questionImprovement : function (questionId, completionId, showXName) {
	
		var controller = this;
		
		if (this.currentView != 'questionImprovement') {
			sqpBackbone.helpers.hideAllPages();
			$("#pageQuestionImprovement").fadeIn();
			$('#questionTab').removeClass('unselectedtab').addClass( 'selectedtab');
			this.currentView = 'questionImprovement';
		}
		
		this.currentImprovementId = questionId;
		this.qImprovementView  = false;
		$('#qImprovementDetailContainer').html(ich.improvementSelectedIntro());
		
		// Create an instance of our question model object
		var question= new sqpBackbone.models.questionItem;
		question.url = question.url + questionId + '&randForRefresh=' + Math.random();
		
		$("#qImprovementBreadCrumb").html('Loading...');
		$("#questionImprovementLoading").show();
		$("#questionImprovementContainer").hide();
		$("#qImprovementQualityPrediction").html('Loading...');
		
		
		var showImprovements = function (qualityInfo) {
			controller.qImprovementView = new sqpBackbone.views.questionImprovementView({
				el: $('#questionImprovementContainer'),
				model: question, 
				completionId : completionId,
				qualityInfo : qualityInfo
			});
			
			if(showXName) {
				controller.qImprovementView.showXName(showXName);
			}
		}
		
		var showPrediction = function () {
			var keyList = 'question_reliability,question_validity,question_quality';
		
			if(completionId) {
				var completionPart = '&completionId=' + completionId;
			} else {
				var completionPart = '';
			}
			
			$.ajax({
						url: '/sqp/api/renderPredictions/?questionId=' 
						     + questionId 
						     + completionPart
							 + '&predictionKeyList=' 
							 + keyList,
						success: function(data){
						 	
						 	if (!data['success']) {
						 		$("#qImprovementQualityPrediction").html(data['meta']['general_error']);
						 	} else {
						 		var context = data['payload'];
						 		context['predictionTitle'] = question.getPredictedByInfo(completionId);
						 		$("#qImprovementQualityPrediction").html(ich.questionQualityPredictionOverview(context));
						 		showImprovements(data['payload']);
						 	}
						},
						dataType : 'json'
					}
				 );
		};

		// load json into out question model
		question.fetch({
			success: function(msg){
				
				
				$("#qImprovementBreadCrumb").html(question.getPredictedByInfo(completionId));
				$("#qImprovementBreadCrumb").attr('href',question.getPredictedByHref(completionId));
				
				controller.updateQuestionBreadCrumb(question);
				showPrediction();
				
				
			}, 
			error : function () {
				alert('There was an error reaching the server. Please check your internet connection and try again.');
				/* Go back to the page before which should be the already loaded question list */
			
			}
		});
	},
	myQuestionImprovementDetail : function (questionId,xName) {
		return this.questionImprovementDetail(questionId,0, xName);
	
	},
	questionImprovementDetail : function questionImprovementDetail(questionId,completionId, xName) {
	
		if (this.currentView != 'questionImprovement' || this.currentImprovementId != questionId) {
			//If the parent view is not loaded we pass a call back to this function 
			//for to be called when all of the improvements are loaded
			this.questionImprovement(questionId, completionId, xName);
		} else {
			this.qImprovementView.showXName(xName);
		}
	},
	help: function(){
		alert("show help");
	},
	about: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'about';
		$("#pageAbout").fadeIn();
		$('#aboutTab').removeClass('unselectedtab').addClass( 'selectedtab');
	},
    faq: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'about';
		$("#pageFAQ").fadeIn();
		$('#faqTab').removeClass('unselectedtab').addClass( 'selectedtab');
	},
	settings: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'settings';
		$("#pageSettings").fadeIn();
	},
	studies: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'studies';
		$("#pageStudies").fadeIn();
		$('#studiesTab').removeClass('unselectedtab').addClass( 'selectedtab');
		
		this.studyListView = new sqpBackbone.views.studyListView({
				el: $('#pageStudies')
			});
	},
	showEditStudy : function (study, onSavedCallback) {
		
		var valid = true;
		var warningNodes=['studyName','studyCompany'];
		var i, node, errorNode, message;
		
		var invalidate = function(){
			valid=false;
			nodeError.html(message);
			nodeError.fadeIn();
			node.addClass('invalid');
		}
		//Assign focus in and out handlers to discourage ESS like names
		for (i=0; i< warningNodes.length; i++) {
			node= $( '#' + warningNodes[i]);
			nodeError  = $( '#' + warningNodes[i] + 'Error');
			node.focusout(function(node, nodeError){
				return function(){
					var name = jQuery.trim(node.val());
					var unadvisedNames=["ess","european social survey"]
					if (unadvisedNames.indexOf(name.toLowerCase()) >= 0){
						nodeError.html('All ESS questions are already available in the SQP database. In order to prevent duplicate studies we suggest you search for your questions of interest in the database.');
						nodeError.fadeIn();
						node.addClass('invalid');
						node.addClass('warning');
						nodeError.addClass('warning');
					}
				};
			}(node, nodeError));
			
			node.focusin(function(node, nodeError){
				return function(){
					nodeError.hide();
					node.removeClass('warning');
					nodeError.removeClass('warning');
					node.removeClass('invalid');
				};
			}(node,nodeError));
			
		}
				
		var clearErrors = function(){
			$('#studyNameError').hide();
			$('#studyCompanyError').hide();
			$('#studyYearError').hide();
			$('#studyCountryError').hide();
			$('#studyName').removeClass('invalid');
			$('#studyCompany').removeClass('invalid');
			$('#studyYear').removeClass('invalid');
			$('#studyCountry').removeClass('invalid');
			$('#studyName').removeClass('warning');
			valid = true;
		}
		
		var onClose = function(){
			clearErrors();
			$('.studyName').val("");
			$('.studyCompany').val("");
			$('.studyYear').val("");
			$('.studyCountry').val("");
		}
		
		var onSaveClick =  function(){
						var studyName = jQuery.trim($('#studyName').val());
						var studyCompany = jQuery.trim($('#studyCompany').val());
						var studyYear = jQuery.trim($('#studyYear').val());
						var studyCountry = jQuery.trim($('#studyCountry').val());
						var forbiddenNames = ['fake', 'test', 'proba', 'prova', 'prueba', 'demo', 'new', 'nova', 'own', 'mine', 'try', 'versuch', 'probe', 'sqp', 'survey quality predictor', 'question'];
						var pattern = new RegExp("[A-Za-z0-9]");
												
						clearErrors();
						
						if(studyName == '') {
							node= $('#studyName');
							nodeError=$('#studyNameError');
							message ='This value is required';
							invalidate();
						}else if (forbiddenNames.indexOf(studyName.toLowerCase()) >= 0 || studyName.length<1 || !$.isNaN(studyName) || 
							 !pattern.test(studyName)){
							//invalid study name
							node= $('#studyName');
							nodeError=$('#studyNameError');
							message ='Please use a meaningful study name. For testing the program you can use the SQP Demo.';
							invalidate();
						}else if(studyName == studyCompany && studyCompany == studyYear && studyYear==studyCountry){
							//all boxes have the same value and is not empty
							
						} 
						if(studyCompany == '') {
							node= $('#studyCompany');
							nodeError=$('#studyCompanyError');
							message ='This value is required';
							invalidate();
						}
						if(studyYear == '') {
							node= $('#studyYear');
							nodeError=$('#studyYearError');
							message ='This value is required';
							invalidate();
						}
						if(studyCountry == '') {
							node= $('#studyCountry');
							nodeError=$('#studyCountryError');
							message ='This value is required';
							invalidate();
						}
						
						
						if(valid) { 
							if(study) {
								var model = study;
							} else {
								var model = new sqpBackbone.models.studyItem();
							}
							
							model.set({name: studyName,
									   company: studyCompany,
									   year: studyYear,
									   country: studyCountry});
							model.save(model.toJSON(), {
								error: function(model, response){ 
									alert('There was an error contacting the server and the item could not be saved. Please check your connection and try again.');
								},
								success: function(model, response){
									model.set({'id' : response.payload.id})
									if (response.success == "1"){
										/* We refresh the study lists */ 
										sqpBackbone.shared.studiesfitted.fetch({
											error: function(err){ alert("error: " + JSON.stringify(err));}
										});
										sqpBackbone.shared.studies.fetch({
											error: function(err){ alert("error: " + JSON.stringify(err));},
											success: function(){ 
												$("#editStudy").dialog("close");
												/* We call the callback which was passed to showAddStudy */
												if (onSavedCallback) {
													onSavedCallback(model);
												}
											}
										});
										
									} else {
										//Send the error off to the error handler
										sqpBackbone.helpers.handleServerError(response);
									}		 
								}	
							});
						}
					};
					
		clearErrors();		
		//Edit	
		if(study) {
			
			$("#editStudy").dialog({
				autoOpen: true,
				height: 500,
				width: 450,
				modal: true,
				resizable : false,
				title : 'Edit Study',
				buttons: { /* jQuery dialog creates and binds these buttons */
					'Save Study' : onSaveClick
				},
				close: onClose
			});
			
			$('#studyName').val(study.get('name'));
			$('#studyCompany').val(study.get('company'));
			$('#studyYear').val(study.get('year'));
			$('#studyCountry').val(study.get('country'));

		//New	
		} else {
			
			onClose() //Cleans everything
			
			$("#editStudy").dialog({
				autoOpen: true,
				height: 500,
				width: 450,
				modal: true,
				resizable : false,
				title : 'Add New Study',
				buttons: { /* jQuery dialog creates and binds these buttons */
					'Create Study' : onSaveClick
				},
				close: onClose
			});
		}
	},
	search: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'search';
		$("#pageSearch").fadeIn();
		
		$('#searchTab').removeClass('unselectedtab').addClass( 'selectedtab');
	},
	home: function(){
		sqpBackbone.helpers.hideAllPages();
		this.currentView = 'home';

		var assignedQuestions = new sqpBackbone.collections.assignedQuestionsList();
		
		assignedQuestions.fetch({
			success: function() {
				if(assignedQuestions.length > 0) {
					//Show a notice about assignment
					$('#assignmentNotice').show();
					
					sqpBackbone.helpers.updateAssignedCount(assignedQuestions);
					
					
					$('#removeAssigment').button();
					$('#assignedQuestionListButton').button();
					
				}

				$('#sqpmain').fadeIn();
				$('#homeTab').removeClass('unselectedtab').addClass('selectedtab');
		
			},
			error: function() {
				alert('There was an error contacting the server.');
			}
         });
	}
});

