// Coding list
sqpBackbone.models.studyItem = Backbone.Model.extend({
	url: '/sqp/api/study?studyId=',
	initialize : function (attributes) {
		if (attributes.url) {
			this.url = attributes.url;
		}
	}
});