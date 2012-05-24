
	/// View for a single question row item in the assigned question list
	sqpBackbone.views.assignedQuestionRowView = Backbone.View.extend({
		initialize: function() { 
			this.render();
			$(this.el).css('cursor' , 'pointer');
		},
		events : {
			'click' : 'handleItemClick',
			'mouseover' : 'handleOver',
			'mouseout' : 'handleOut'
		},
		handleItemClick : function (event) {
			window.location.hash = this.model.getCodingHref();
		},
		handleOver : function () {
			$('.overQuestionRow').removeClass('overQuestionRow');
			$(this.el).addClass('overQuestionRow');
		},
		handleOut : function () {
			$(this.el).removeClass('overQuestionRow');
		},
		tagName: 'tr',
		render: function(){ 
			// render output with ICanHaz.js template
			$(this.el).html(ich.assignedQuestionRow(this.model.toJSON()));
			return this;
		}
	});