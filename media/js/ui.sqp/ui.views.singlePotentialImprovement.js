	/// View for a single question row item in the variable  list for improvements
	sqpBackbone.views.singlePotentialImprovement = Backbone.View.extend({
		
		initialize: function() { 
			this.render();
		},
		tagName: 'tr',
		render: function(){ 
			// render output with ICanHaz.js template
			
			
			$(this.el).html(ich.singlePotentialImprovement(this.model.toJSON()));
			
			return this;
		},
	  	flash : function () {
	  		var origColor = $(this.el).css('backgroundColor');
	  		var el = this.el
	  		$(el).animate({
	  			backgroundColor : '#F2D06D'
	  		}, 1500);
	  		
	  		setTimeout(function() {
	  			$(el).animate({
		  			backgroundColor : origColor
		  		}, 1500);
	  		}, 2500);
	  	}
	});
	