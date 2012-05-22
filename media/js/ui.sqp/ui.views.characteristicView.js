
	///////////////////////
	// Characteristic View
	///////////////////////
	sqpBackbone.views.characteristicView = Backbone.View.extend({
		
		timeStarted : false,
		timeFinished : false,
		characteristicId : false,
		canEdit : false,
		completionId : 0,
		initialize: function() {
		
			 this.canEdit = this.options.canEdit;
			 this.completionId = this.options.completionId;
			 this.render();
			 this.timeStarted = new Date().getTime();
			 this.characteristicId = this.model.get('characteristicId');
			 
			 //Set the characteristicId as a global
			 sqpBackbone.app.currentCharacteristicId = this.characteristicId;
			 //Highlight asap in the table on the right
			 sqpBackbone.app.markCurrentRow();
			 },
	    
		render: function(){
			//Set up the suggested value before rendering
			if(!this.model.get('hasBeenAnswered') 
			   && this.model.get('autoFillSuggestion')
			   && this.model.get('hasSuggestion')) {
			   this.model.set({'choice': this.model.get('suggestion')});
			   var isAutoFilled = true;
			   
			   if(this.model.get('characteristicWidget') == "radiobuttons") {
			   		var options = this.model.get('choiceOptions');
					var choice = this.model.get('suggestion');
					for (var i = 0; i < options.length; i++) {
						if (options[i].labelCode == choice) {
							options[i].labelSelected = true;
						}
					}
					this.model.set({'choiceOptions' : options});
			   }
			   
			} else {
			   var isAutoFilled = false;
			}
			
			// render output with ICanHaz.js template
			 var the_jSon = this.model.toJSON()
			 the_jSon['characteristicDescIntro'] = this.model.characteristicDescIntro();
			 
			 if (the_jSon['characteristicDescIntro'] != this.model.get('characteristicDesc')) {
			 	the_jSon['showMore'] = true;
			 } else {
			 	the_jSon['showMore'] = false;
			 }
			 
			 the_jSon['isAutoFilled'] = isAutoFilled;
			 
			 the_jSon['canEdit'] = this.canEdit;
			 
			 //console.log(the_jSon);
			 
			 var view = this;
			
			// Depending on the type of characteristicWidget we 
			// render the for in a different way
			 
			switch( the_jSon.characteristicWidget ) {
				case "radiobuttons":	
				
					$(this.el).html(ich.characteristicRadioTemplate(the_jSon));
					
					/* Bind radio options to the buttonSubmit */
					this.$('.optionRadio').mouseup(function(event) {
					
						$(this).attr('checked', true);
						view.buttonSubmit();
					});
					
					
					/* Bind radio labels to the buttonSubmit */
					this.$('.optionLabel').mouseup(function(event) {
					     
						var label_for = $(this).attr('for');
						$('#' + label_for).attr('checked', true);
						view.buttonSubmit();
					});
					
					/* Bind the enter key on the radio button*/
					this.$('.optionRadio').keydown(function(event){
						if (event.keyCode == '13') {
							event.preventDefault();
							// Give the browser 20 seconds to select the correct
							// radio then we call the submit function
							setTimeout(function() {
								view.buttonSubmit();
							}, 20);
						}
					})
					
					this.$('.optionRadio').focus();
					break;
				case "numeric":
					
					$(this.el).html(ich.characteristicNumericTemplate(the_jSon));
					
					this.$('.characteristicNumericInput').keydown(function(event) {
						if (event.keyCode == '13')  { /* Enter key */
					     	event.preventDefault();
							view.buttonSubmitNumeric();
					   	}
					});
					this.$('.characteristicNumericInput').focus();
					
					break;
				case "just_a_text":	
					
					if (the_jSon.characteristicShortName == "question") {
						
						$(this.el).html(ich.characteristicWelcomeTemplate(the_jSon));
					
					} else {
						
						$(this.el).html(ich.characteristicTextTemplate(the_jSon));
					}
					break;
				default:
					//alert("No template avaliable for this type of characteristicWidget");
			}
			
			this.$('.btn').button();
			
			
			//Show more information about the suggestion after the rendering is complete
			
			if (this.model.get('hasSuggestion')) {
				var suggestion = this.model.get('suggestion')
				
				if (this.model.get('characteristicWidget') == 'radiobuttons'){
					var choiceOptions = this.model.get('choiceOptions')
					for (var i = 0; i < choiceOptions.length ; i ++){
						if(choiceOptions[i]['labelCode'] == suggestion) {
							var suggestion_as_text = choiceOptions[i]['labelName'];
						}
					}
				} else {
					var suggestion_as_text = this.model.get('suggestion');
				}
				
				if (this.model.get('hasExplanation')) {
				    var	explanation =  this.model.get('suggestionExplanation');
					
					explanation = '<div style="width:45%">' + explanation + '</div>'; 
					
				} else {
					var explanation = '';
				}
				
				this.$('.suggestionInfo').html ('<p>Suggested value: ' + suggestion_as_text + '</p>' + explanation);
			}
			
			
			//Hide the loading div 
			$('.editCodingLoading').hide();
			
			sqpBackbone.helpers.scrollToTop();
			
			return this;
	  	},
	  	events: {
			"click .buttonPrevious"           	: "buttonPrevious",
			"click .buttonSubmit"              	: "buttonSubmit",
			"click .buttonSubmitNumeric"		: "buttonSubmitNumeric",
			"click .buttonSubmitWelcome"		: "buttonSubmitWelcome",
			"click .hideFullDesc"				: "hideFullDesc",
			"click .characteristicDescIntro, .readFullDesc"	: "showFullDesc"
		},
		buttonSubmit: function(){ 
			
			if (this.completionId) {
				return this.goNext()
			}
			
			//Radio submit
			
			if (!this.canEdit) {
				//Show the wait for chars
				sqpBackbone.helpers.showCharacteristicWait();
				this.goNext();
			} else {
				// Update the model
				var currentSelected = $("[name='choiceOptions']:checked").val();
				if (!currentSelected) {
					this.showError('Please select an option to continue.');
				}
				else {
					//Show the wait for chars
					sqpBackbone.helpers.showCharacteristicWait();
					
					var currentOption = this.model.get('choiceOptions');
					var currentLableCode = "";
					$.each(currentOption, function(index, val){
					
						if (val.labelId == currentSelected) {
							currentOption[index].labelSelected = 'true';
							currentLableCode = val.labelCode;
							
						}
						else {
							currentOption[index].labelSelected = 'false';
						}
					});
					this.model.set({
					
						choiceOptions: currentOption,
						choice: currentLableCode
					
					});
					this.saveModel();
				}
			}
			
			
		},
		buttonPrevious : function () {
		
			if (this.completionId) {
				var completionPart = '&completionId=' + this.completionId;
			} else {
				var completionPart = '';
			}
			
			sqpBackbone.helpers.loadCharacteristicCoding("/sqp/api/coding/?questionId=" 
								+ this.model.get('questionId')
								+ "&beforeCharacteristicId=" 
								+ this.model.get('characteristicId')
								+ completionPart, this.completionId );
		},
		buttonSubmitNumeric: function(){ 
			if (this.completionId) {
				return this.goNext()
			}
			
			// Update the model
			var currentValue = $("[name='numeric']").val();
			if (!/^\d+$/.test(currentValue)) /* reg exp numeric */{
				this.showError('Please enter a valid number to continue.');
			} else {
				//Show the wait for chars
				sqpBackbone.helpers.showCharacteristicWait();
				//	alert("the current value: " + currentValue);
				this.model.set({ choice : currentValue});
				this.model.set({ hasBeenAnswered : 'True'});
				this.saveModel();
			}
		},
		buttonSubmitWelcome : function(){
			//Show the wait for chars
			sqpBackbone.helpers.showCharacteristicWait();
				
			sqpBackbone.helpers.loadCharacteristicCoding("/sqp/api/coding/?questionId=" + this.model.toJSON().questionId + "&fromCharacteristicId=" + this.model.toJSON().characteristicId);
		},
		showError : function (errorText) {
			
			this.$('.errorInfo').html(errorText).show();
			this.$('.valueIncorrectIcon').show();
			this.$('.characteristicNumericInput').css({'border' : '1px solid #C83C00', 'padding' : '2px'});	
			this.$('.characteristicNumericInput').focus();
		}, 
		showFullDesc : function(event) {
			event.stopPropagation();
			event.preventDefault();
			this.$('.characteristicDescFull').css('visibility','visible');
			this.$('.characteristicDescFullShadow').fadeTo('fast', 0.4);
			this.$('.characteristicDescFullShadow').height(this.$('.characteristicDescFull').height());
			this.$('.characteristicDescFullShadow').width(this.$('.characteristicDescFull').width());
			this.$('.characteristicDescFullShadow').css('visibility','visible');
		},
		hideFullDesc : function() {
			this.$('.characteristicDescFull').css('visibility','hidden');
			this.$('.characteristicDescFullShadow').css('visibility','hidden');
		},
		saveModel : function saveModel() {
			// Save
			this.model.url = this.model.toJSON().url;
			this.timeFinished = new Date().getTime();
			
			this.model.set({
				'secondsTaken': (this.timeFinished - this.timeStarted) / 1000
			 });
			var view = this;
			
			this.model.save(this.model.toJSON(), {
				error: function(model, response){ 
				    alert('There was an error contacting the server and the coding could not be updated. Please check your connection and try again.');
					$('.editCodingLoading').hide();
				},
				success: function(model, response){
					if (response.success == "1"){
						var qAdded = sqpBackbone.helpers.responseHandler(response);
						sqpBackbone.helpers.loadCharacteristicCoding("/sqp/api/coding/?questionId=" + qAdded.questionId + "&fromCharacteristicId=" + qAdded.characteristicId);
						
						setTimeout(function ()  {
							sqpBackbone.helpers.reloadCodings(qAdded.questionId);
						}, 190);
					} else {
						view.showError(response.error_message);
						$('.editCodingLoading').hide();
					}		
				}	
			});
		},
		goNext : function () {
			if (this.completionId) {
				var completionPart = '&completionId=' + this.completionId;
			} else {
				var completionPart = '';
			}
			
			
			sqpBackbone.helpers.loadCharacteristicCoding("/sqp/api/coding/?questionId=" + this.model.get('questionId') 
				 										+ "&fromCharacteristicId=" + this.model.get('characteristicId')
				 										+ completionPart, this.completionId);
		}
  	});