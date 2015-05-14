
	
	// **New Question Detail view
	sqpBackbone.views.questionEditView = Backbone.View.extend({
		//These all get converted into jQuery node selectors by class name in mapNodes
		nodes : {
			qEditStudy		 			: null,
			qEditCountry		 		: null,
			qEditLanguage	 			: null,
			qEditRequestForAnswerText   : null,
			qEditIntroText			    : null,
			qEditAnswerOptionsTexts     : null,
			qEditQuestionItemCode		: null,
			qEditQuestionItemName		: null,
			qEditQuestionDescription	: null,
			qEditPleaseCorrectErrors	: null
		},
		validationRules : [{input 		: 'qEditStudy',
		                    required 	: true,
							is_detail   : true},
						   {input 		: 'qEditCountry',
						    is_detail   : true,
		                    required 	: true},
						   {input 		: 'qEditLanguage',
						    is_detail   : true,
		                    required 	: true},
						   {input 		: 'qEditQuestionItemCode',
						    is_detail   : true,
		                    required 	: true,
							maxLength	: 8},
						   {input 		: 'qEditQuestionItemName',
						    is_detail   : true,
		                    required 	: false,
							maxLength	: 8},
						   {input 		: 'qEditQuestionDescription',
		                    required 	: true,
							is_detail   : false,
							maxLength	: 300},
						   {input 		: 'qEditRequestForAnswerText',
						    is_detail   : false,
		                    required 	: true},
						   {input 		: 'qEditAnswerOptionsTexts',
						    is_detail   : false,
		                    required 	: false}
							],
		initialize: function() { 
			
			this.render();
		},
		lockSubmitButton : false,
	  	events: {
			"click .buttonSaveQuestion"          			: "saveQuestion",
			"click .qEditAddNewStudy"           			: "addNewStudy",
			"change .qEditLanguage"     	       			: "updateLanguage"
		},
		showInputError : function showInputError(inputNode, errorNode, message) {
			inputNode.addClass('invalid');
			errorNode.html(message);
			errorNode.fadeIn();
		},
		validate : function validate(nodeName) {
			
			var formValid = true;
			
			var canEditDetails = this.model.get("canEditDetails");
			
			for (var i = 0; i < this.validationRules.length; i ++) {
				
				 var rules 		= this.validationRules[i];
				 var inputNode  = this.nodes[rules['input']];
				 var val   		= jQuery.trim(inputNode.val());
				 var errorNode  = this.$( '.' + rules['input'] + 'Error');
				 var valid      = true;
				 
				 if (rules['is_detail'] && !(canEditDetails)) {
				 	//skip over detail validation if the user 
					//can't edit details like country/language/item
				 	continue;
				 }
				 
				 //Check if validate(node) we were called with only one node 
				 //We only change the error status message for that node
				 if(nodeName != undefined && rules['input'] != nodeName) {
				 	var changeErrorStatus = false;
				 } else {
				 	var changeErrorStatus = true;
				 }
				
				 if(rules['required'] && val == '') {
				 	formValid = false;
				
					if (changeErrorStatus == true) {
						this.showInputError(inputNode, errorNode, 'This field is required');
					}
					continue;
				 }
				 
				  if(rules['maxLength'] && val.length > rules['maxLength']) {
				 	formValid = false;
					if (changeErrorStatus == true){
						this.showInputError(inputNode, errorNode, 'This value is too long. It must be ' + rules['maxLength'] + ' characters or shorter' );
					} 
					continue;
				 }
				 
				 /* not in use currently 
				 if(rules['multiLine'] && val.indexOf('\n') == -1) {
				 	formValid = false;
					if (changeErrorStatus == true){
						this.showInputError(inputNode, errorNode, 'You must enter at least two options. Each option must be on its own line.');
					} 
					continue;
				 }
				 */
				 
				//We only get here if the input passes all of the rule checks
			 	inputNode.removeClass('invalid');
				errorNode.fadeOut();
				 
			}
			
			
			if(formValid) {
				this.nodes.qEditPleaseCorrectErrors.fadeOut();
			} else if(nodeName == undefined){
				this.nodes.qEditPleaseCorrectErrors.fadeIn();
			}
			
			return formValid;
		},
		saveQuestion : function saveQuestion() {
			var model = this.model;
			var self =this;
			//Prevent double saving from clicks
			if (self.lockSubmitButton) return;
			self.lockSubmitButton = true;
			
			if(!this.validate()) {
				self.lockSubmitButton = false;
				return;
			}
			
			model.set({'requestForAnswerText' : this.nodes.qEditRequestForAnswerText.val(),
					   'introText' : this.nodes.qEditIntroText.val(),
					   'answerOptionsTexts' : $.trim(this.nodes.qEditAnswerOptionsTexts.val()).split("\n")})
		
			
			if (model.get("canEditDetails")) {
				model.set( {'countryIso' 		: this.nodes.qEditCountry.val(),
					   		'languageIso' 		: this.nodes.qEditLanguage.val(),
					   		'studyId' 			: this.nodes.qEditStudy.val(),
							'itemCode' 			: this.nodes.qEditQuestionItemCode.val(),
							'itemName' 			: this.nodes.qEditQuestionItemName.val(),
							'itemDescription' 	: this.nodes.qEditQuestionDescription.val()
							})
			}
			model.save(null, {
				error: function(model, response){ 
					self.lockSubmitButton = false;
					alert('There was an error contacting the server and the question could not be saved. Please check your connection and try again.');
				},
				success: function(model, response){
					self.lockSubmitButton = false;
					if (response.success == "1"){
						//Do not pass as a "not success" unless we want a popover with the server error message 
						if(model.get("repeated_code")){
							inputNode=self.nodes.qEditQuestionItemCode;
							errorNode=self.$( '.' +'qEditQuestionItemCodeError');
							self.showInputError(inputNode, errorNode, 'This question name is already in use in the study selected, please choose a different one.');    
						}else{
						    //Clear the question if it was previously cached
						    sqpBackbone.app.clearCachedQuestion();
						    window.location.hash = "#questionCoding/" + model.get('id');
						}
					} else {
						//Send the error off to the error handler
						sqpBackbone.helpers.handleServerError(response);
					}		 
				}	
			});
		},
		render: function(){
			
			
			$("#qEditBreadCrumb").html(this.model.getTitle());
			$("#qEditBreadCrumb").attr('href', '#question/' + this.model.get('id'));
			
			if(!this.model.get("canEditText")) {
				//Client side check, there is a server side check as well
				alert('Operation not permitted');
				return;
			}
			
			// render output with ICanHaz.js template
			var context = this.model.toJSON()
			var model = this.model;
			var view = this;
			context['answerOptionsTextBlock'] = function () {
				return model.answerOptionsTextBlock();
			}
			
			$(this.el).html(ich.questionEdit(context));
			
			 if (this.model.get('rtl') == true) {
		    	this.setInputDir('rtl');
		    } else {
		    	this.setInputDir('ltr');
		    }
			
			//Hide all of the error message containers
			$('.inputErrorMessage, .inputErrorMessageForTextArea, .qEditPleaseCorrectErrors').hide();
			
			//Map our dom nodes to jQuery objects for this view
			sqpBackbone.helpers.mapNodes(this);
			
			//Map our required inputs
			this.requiredInputs = [ this.nodes.qEditStudy,
									this.nodes.qEditCountry,
									this.nodes.qEditLanguage,
									this.nodes.qEditQuestionItemName,
									this.nodes.qEditQuestionDescription,
									this.nodes.qEditRequestForAnswerText,
									this.nodes.qEditAnswerOptionsTexts]
			
			this.$('.btn').button();
			
			
			
			if(this.model.get("canEditDetails")) {
				this.renderStudySelect();
				this.renderCountrySelect();
				this.renderLanguageSelect(); 
				
				//Bind our study select
				sqpBackbone.shared.studiesfitted.bind('refresh', function() {
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
			}
			
			//Apply our validation rules on change
			for (var i = 0; i < this.validationRules.length; i++) {
				var rules = this.validationRules[i];
				var inputNode  = this.nodes[rules['input']];
				
				//Using jQuery bind
				//The second argument {inputNodeName: rules['input']} becomes the event data
				inputNode.bind('change', {inputNodeName: rules['input']}, function(event) {
					 view.validate(event.data.inputNodeName);
				});
			}
			
			return this;	
	  	},
	  	updateLanguage : function () {
	  		//When the language input gets changed, we have to set the right-to-left direction 
	  		//for the inputs and model for languages like hebrew and arabic to work correctly
		    var val = this.$('.qEditLanguage').val();
		    if (val == 'arb' || val == 'heb') {
		    	this.model.set({'rtl': true});
		    	this.setInputDir('rtl');
		    } else {
		    	this.model.set({'rtl': false});
		    	this.setInputDir('ltr');
		    }
	  	},
	  	setInputDir : function (dir) {
	  		//Sets the text direction for the inputs
	  	    var textInputs = ['.qEditRequestForAnswerText', '.qEditAnswerOptionsTexts', '.qEditIntroText'];
	  		for (var i = 0;  i < 3; i ++) {
	  		 	var inputName = textInputs[i];
	  			this.$(inputName).attr('dir', dir);
	  		}
	  	},
		setItemEditable : function (canEdit) {
			 if(canEdit) {
			 	this.nodes.qEditQuestionItemCode.removeAttr('disabled');
				this.nodes.qEditQuestionDescription.removeAttr('disabled');
			 } else {
			 	this.nodes.qEditQuestionItemCode.attr('disabled', 'disabled');
				this.nodes.qEditQuestionDescription.attr('disabled', 'disabled');
			 }
		},
		addNewStudy : function addNewStudy() {
			
			var view = this;
			
			//Delegate this action to the global add study function
			sqpBackbone.app.showEditStudy(false, function onStudyAdded(model) {
				view.nodes.qEditStudy.val(model.get('id'));
			});
			
		},
		renderStudySelect : function renderStudySelect() {
			var view = this;
			this.nodes.qEditStudy.children().remove();
			
			this.nodes.qEditStudy.append('<option value=""> -- select -- </option>');
			
			//Add in options
			sqpBackbone.shared.studiesfitted.each(function(study) {
				 if(study.get('id') == view.model.get('studyId')) {
				 	var selected = 'selected="selected"'
				 } else {
				 	var selected = '';
				 }
				 view.nodes.qEditStudy.append('<option value="' + study.get('id') + '" ' + selected +'>' + study.get('name') + '</option>');
			});
		},
		renderCountrySelect : function renderCountrySelect() {
			var view = this;
			this.nodes.qEditCountry.children().remove();
			//Add in options
			
			this.nodes.qEditCountry.append('<option value=""> -- select -- </option>');
			sqpBackbone.shared.countries.each(function(country) {
				 if(country.get('iso') == view.model.get('countryIso')) {
				 	var selected = 'selected="selected"'
				 } else {
				 	var selected = '';
				 }
				 view.nodes.qEditCountry.append('<option value="' + country.get('iso') + '" ' + selected +'>' + country.get('name') + '</option>');	
			});
		},
		renderLanguageSelect : function renderLanguageSelect() {
			var view = this;
			this.nodes.qEditLanguage.children().remove();
			//Add in options
			this.nodes.qEditLanguage.append('<option value=""> -- select -- </option>');
			sqpBackbone.shared.languages.each(function(language) {
				 if(language.get('iso') == view.model.get('languageIso')) {
				 	var selected = 'selected="selected"'
				 } else {
				 	var selected = '';
				 }
				 view.nodes.qEditLanguage.append('<option value="' + language.get('iso') + '" ' + selected +'>' + language.get('name') + '</option>');	
			});
		}
		
  	});
	