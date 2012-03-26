

sqpBackbone.models.questionItem = Backbone.Model.extend({
	initialize: function () {
	
	},
	url: '/sqp/api/question?questionId=',
	parse: function(response){
		return sqpBackbone.helpers.responseHandler(response);
	},
	getTitle : function getTitle() {
		
		var title = '';
		
		if (this.get('itemCode')) {
			title += this.get('itemCode');
		}
		
		if (this.get('itemName')) {
			title +=  ' / ' + this.get('itemName'); 
		}
			
		if (this.get('itemDescription')) {
			title +=  ' / ' + this.get('itemDescription');
		}
		
		return title;
		
	}, 
	getShortTitle : function getShortTitle() {
		
		var title = '';
		
		title +=  this.get('studyName') + ' / ';
		
		if (this.get('itemCode')) {
			title +=  this.get('itemCode') + ' / ';
		}
		
		if (this.get('itemName')) {
			title +=  this.get('itemName') + ' / '; 
		}
		
		title += ' ' + this.get('country');

		return title;
		
	}, 
	getIcon : function (icon, title, color) {
		return ich.questionCodedByIcon({
			icon : icon,
			title : title,
			color : color
		}, 'text');
	},
	getCompletion : function getCompletion(completionId) {
		if (this.get('authorizedPrediction') && completionId == this.get('authorizedPrediction')['completionId']) {
			return this.get('authorizedPrediction')
		} else {
			var otherPredictions = this.get('otherPredictions');
			
			for (var i = 0; i < otherPredictions.length; i ++) {
				if (otherPredictions[i]['completionId'] == completionId) return otherPredictions[i];
			} 
		}
	},
	getByInfo : function (completionId, itemType) {
		if (!completionId) {
			return this.getIcon('mine', 'My ' + itemType, '#86BD90');
		} else {
			completion = this.getCompletion(completionId);
			
			if (completion.isAuthorized) {
				return this.getIcon('a', 'Authorized ' + itemType, '#9FB1C2');
			} else {
				return this.getIcon('u1', 'User ' + itemType + ' by ' + completion.user, '#295F6D') ;
			}
		} 
	},
	getCodedByInfo : function (completionId) {
		return this.getByInfo(completionId, 'Coding');
	},
	getPredictedByInfo : function (completionId) {
		return this.getByInfo(completionId, 'Quality Prediction');
	},
	getPredictedByHref : function (completionId) {
		if (completionId) {
			return '#questionPrediction/' + this.get('id') + '/' + completionId;
		} else {
			return '#questionPrediction/' + this.get('id');
		}
	},
	getCodingHref: function (completionId) {
		if (completionId) {
			return '#questionCoding/' + this.get('id') + '/' + completionId;
		} else {
			return '#questionCoding/' + this.get('id');
		}
	},
	getImprovementHref: function (completionId) {
		if (completionId) {
			return  '#questionImprovement/' + this.get('id') + '/' + completionId;
		} else {
			return  '#questionImprovement/' + this.get('id');
		}
	},
	answerOptionsTextBlock : function () {
		try {
			return this.get('answerOptionsTexts').join("\n");
		} catch(e) {
			return '';
		}
	}
});