	
	///  The Study List Table
	sqpBackbone.views.studyListView = Backbone.View.extend({
		//These all get converted into jQuery node selectors by class name in mapNodes
		nodes : {
			studyListTable			:null,
		},
		events : {
			'click .studyListAddNew' : 'addStudy'
		},
		initialize: function() {
			var view = this;
			
			//Map our dom nodes to jQuery objects for this view
			sqpBackbone.helpers.mapNodes(this);
		
			//Bind our study list to the shared study collection
			sqpBackbone.shared.studies.bind('refresh', function() {
				view.render();
			});
	
			view.render();
			
		},
		addStudy : function () {
			sqpBackbone.app.showEditStudy();
		},
		render: function(){
		
			var view = this;
			//Remove old rows
			$('td', this.nodes.studyListTable).remove();
			
			//Add in new rows to the table body
			sqpBackbone.shared.studies.each(function(study){
				var studyRowView = new sqpBackbone.views.studyRowView({
					model: study
				});
	
				view.nodes.studyListTable.append(studyRowView.el);
			});
			
			return this;
	  	}
  	});