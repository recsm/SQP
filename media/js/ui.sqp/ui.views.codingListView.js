
	// **NEW
	/// The view for a Coding list
	sqpBackbone.views.codingListView = Backbone.View.extend({
		
		initialize: function() { this.render();},
		
		render: function(){
			$("#codinglist").html("");
			var fromCharacteristicId = 0;
			var questionId = 0;
			var view = this;
			
			this.collection.each(function(codingItem) {
				
				fromCharacteristicId = codingItem.toJSON().characteristicId;
				questionId =  codingItem.toJSON().questionId;
				
				 var itemView = new sqpBackbone.views.codingItemView({model: codingItem, completionId : view.options.completionId});
				 this.$("#codinglist").append(itemView.el);	
				 
			});
			
			$('#codingList').show();
			$('#codingListWelcome').hide();
			
			sqpBackbone.app.markCurrentRow();
			
			return this;
	  	}
  	});