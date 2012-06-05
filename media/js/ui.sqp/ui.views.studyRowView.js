
	/// View for a single study row item in the study list
	sqpBackbone.views.studyRowView = Backbone.View.extend({
		
		initialize: function() { this.render();},
		tagName: 'tr',
		events : {
			'click .studyItemDelete' : 'confirmDelete',
			'click .studyItemEdit' : 'editStudy'
		},
		render: function(){ 
			// render output with ICanHaz.js template
			$(this.el).html(ich.singleStudyListItem(this.model.toJSON()));
			return this;
		},
		confirmDelete: function () {
			var view = this;
			var confirmed = confirm('Do you really want to delete the study "' + this.model.get('name') + '"? All questions in this study will also be deleted.');
			if(confirmed) {
				this.model.destroy({
					error : function(err) {
						alert(err);
					},
					success : function(model,response) {
						
						if(response.success == 1) {
							//Refresh the shared studies objects
							sqpBackbone.shared.studies.fetch();
							
							//Remove this view
							view.remove();
						} else {
						    alert('ERROR ' + response);
						}
					}
				});
			}
		},
		editStudy : function editStudy() {
			sqpBackbone.app.showEditStudy(this.model);
		}
		
	});