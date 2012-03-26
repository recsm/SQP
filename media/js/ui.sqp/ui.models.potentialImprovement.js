// MODEL Potential Improvement for a variable
sqpBackbone.models.potentialImprovement = Backbone.Model.extend({
	initialize : function () {
		this.setDerivedProperties();
	},
	setDerivedProperties : function () {
	
		if(this.get('isError'))  { 
			this.set({'color' : 'red'});
		
		} else if(this.get('loaded')) { 
			this.set({'color' : false});
		
		} else {
			this.set({'color' : '#ccc'})
		}
		
		
		if (!this.get('loaded') || this.get('isError')) return;
		
		var qualMax = this.getQualMax();
		this.set({
		 	'qualMax' : qualMax ,
			'potentialImprovement' : Math.round((qualMax  - this.get('questionQuality')) * 1000) / 1000,
			'potentialImprovementVisual' : Math.ceil(((qualMax) - this.get('questionQuality')) * 500)
		});
		
		
		if (this.get('potentialImprovement') > 0) {
			this.set({'hasPotentialImprovement': true});
		}
	
		if(!this.get('isError') && !this.get('hasPotentialImprovement')) {
			this.set({'color':'#888'});
		}
		
		
		
	},
	getQualMax : function () {		
		var max = -99;
		try {
			var qualRange = this.get('qual2');
			for (var i = 0; i < qualRange.length; i++) {
				var value = qualRange[i][1];
				if(value > max) max = value
			}
		} catch (e){
		
		}
		return max;
	}
});
