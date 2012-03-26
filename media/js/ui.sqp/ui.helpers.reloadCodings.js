
// Load Codings List
sqpBackbone.helpers.reloadCodings = function sqpBackbone$reloadCodings(questionId){
	
	//alert("reload");
	$('#charateristicDetailContainerInner').show();
	$('#charateristicDetailContainerInnerWelcome').hide();
	
	var allCodings = new sqpBackbone.collections.codingList;
	allCodings.url = '/sqp/api/questionCodingHistory/?questionId='+questionId ;
	allCodings.fetch({
			error: function(err){ alert("error: " + JSON.stringify(err));},
			success: function(msg){
				hList = new sqpBackbone.views.codingListView({
					collection: allCodings
				});
				
				
			}
	});
	
};
