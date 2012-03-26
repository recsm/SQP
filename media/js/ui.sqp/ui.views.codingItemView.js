

	// **NEW
	// Coding Item view
	sqpBackbone.views.codingItemView = Backbone.View.extend({
		
		initialize: function() { this.render();},
		tagName: 'tr',
		render: function(){ 
			this.model.set({completionId : this.options.completionId});
			$(this.el).html(ich.codingListItem(this.model.toJSON()));
			
			//console.log(this.model.toJSON());
			return this;
		}
		
	});