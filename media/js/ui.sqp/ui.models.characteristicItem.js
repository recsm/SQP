
// Characteristic Model
sqpBackbone.models.characteristicItem = Backbone.Model.extend({
	url: '/sqp/api/characteristic?questionId=',
	parse: function(jsonResponse){		
		//We excpect the view to handle the invalide code 'InvalidCode' so we pass it back
		if (jsonResponse.success == "1" || jsonResponse.error_key == 'InvalidCode'){
			return jsonResponse.payload;
		} else {
			sqpBackbone.helpers.handleServerError(jsonResponse);
		}
	},
	characteristicDescIntro : function () {
		return sqpBackbone.helpers.getTextSnippet(this.get('characteristicDesc'), 200);
	}
});