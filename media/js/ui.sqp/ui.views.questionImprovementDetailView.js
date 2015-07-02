	
	sqpBackbone.views.questionImprovementDetailView = Backbone.View.extend({
		questionId : false,
		xName: false,
		initialize: function() { 
			this.xName = this.options.xName;
			this.questionId = this.options.questionId;
			
			var view = this;
			
			/* Rerender on any model changes */
			this.model.bind('change', function () {view.render();}, this);
			this.render();
		},
		displayError : function () {
			var html  = '<h3 class="errorInfo" style="display:block;width:95%">An Error Occurred loading variable "' + this.model.get('xName') + '"</h3>';
			html += '<p class="errorInfo" style="display:block;width:95%">' + this.model.get('errorMessage') + '</p>';
			$('#qImprovementDetailContainer').html(html);
		},
		render: function(){
			var view = this;
		
			if(this.model.get('isError') == true) {
				this.displayError();
			} else if (! this.model.get('loaded')){
				$('#qImprovementDetailContainer').html('Loading data for variable "'+ this.xName + '"...');
			} else {
				/* TODO: It would be REALLY REALLY good to refactor this to use an icanhaz template */
				var questionQuality = this.model.get('questionQuality');
				currentValue = this.model.get('currentValue');
				var qual2 = this.model.get('qual2');
				var table = $('<table style="clear:both;">');
				$(table).append('<tr style="font-weight:bold;"><td style="width:40%">Choice</td><td colspan="3">Average what if-prediction</td></tr>');
				for (var i = 0; i < qual2.length; i ++) {
					var tr = $('<tr>');
					var label = this.getLabel(qual2[i][0]);
					$(tr).append('<td>' + label + '</td>');
					$(tr).append('<td style="width:10%;">' + qual2[i][1] + '</td>');
					
					var difference = Math.round((qual2[i][1] - questionQuality) * 100) / 100;
					if(difference < 0) {
						width = difference * -1 * 500;
						$(tr).append('<td style="width:15%;border-right:1px solid #ccc;padding-right:0px;"><div style="float:right;margin-top:2px;background-color:#D0735F;width:'
						+ width +'px;height:10px;"></div><div style="float:right;color:#D0735F;padding-right:3px;"> - ' 
						+ (difference * -1) 
						+ ' </div></td><td></td>');
					} else if(difference > 0){
						width = difference * 500;
						$(tr).append('<td style="width:15%;border-right:1px solid #ccc;padding-right:0px;"></td><td style="padding-left:0px;width:35%;"><div style="float:left;margin-top:2px;background-color:#7294C3;width:'
						+ width +'px;height:10px;"></div><div style="float:left;color:#7294C3;padding-left:3px;"> + ' 
						+ difference  
						+ ' </div></td>');
					} else {
						$(tr).append('<td style="width:15%;border-right:1px solid #ccc;padding-right:0px;"></td><td></td>'); //0
					}
			
					$(table).append(tr);
				}

				
				if(this.model.get('variableName') && (this.model.get('xName') != this.model.get('variableName'))) {
					/* Extra info available */
					$(this.el).html('<h3>'+ this.model.get('variableName')+' (' + this.model.get('xName') + ')</h3>');
					
					if(this.model.get('currentValue') != '__none__') {
						$(this.el).append('<p>Current choice: <span style="font-weight:bold">' + this.getLabel(this.model.get('currentValue')) + '</span></p>');
					}
					
				} else {
					/* No extra info available */
					$(this.el).html('<h3>'+ this.model.get('xName')+'</h3>');
				}
				
				
				$(this.el).append(table);
				
				
				if(this.model.get('variableDescription')) {
					var snippet = sqpBackbone.helpers.getTextSnippet(this.model.get('variableDescription'), 200);
					
					if(this.model.get('variableDescription').length > 200) {
						var more = 	 ' <span class="readFullDesc hlinkclass"> more&nbsp;&gt;&gt;</span>';
					} else {
						var more = '';
					}
					
					$(this.el).append('<div class="characteristicDesc characteristicDescImprovements">' 
					                + '<h4>' + this.model.get('variableName') + '</h4>'
					                + '<div class="characteristicDescIntro">' 
					                +  '<p>' + snippet
					                +  more + '</p>'
					                +  '</div>'
					                +  '<div class="characteristicDescImprovementsFull" style="display:none">'
					                + this.model.get('variableDescription')
					                + '</div>'
					                + '</div>');
				 	this.$('.readFullDesc, .characteristicDescIntro').click(function () {
				 		view.$('.characteristicDescIntro').hide();
				 		view.$('.characteristicDescImprovementsFull').show();
				 	})
				}
			}
			return this;
			
	  	},
	  	getLabel : function (code) {
	  		var choiceOptions = this.model.get('choiceOptions');
	  		var label = code;
	  		
	  		for (var i = 0; i < choiceOptions.length; i++) {
	  			if (choiceOptions[i]['labelCode'] == code) {
	  				label = choiceOptions[i]['labelName'];
	  			}
	  		}
	  		
	  		return label;
	  	}
  	});