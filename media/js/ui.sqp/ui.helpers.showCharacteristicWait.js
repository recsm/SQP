
// Load Codings List
sqpBackbone.helpers.showCharacteristicWait = function sqpBackbone$showCharacteristicWait(questionId){
	
	$('.editCodingLoading').show();
	$('.editCodingLoadingContent').fadeTo('fast', .5, function() {});
	
	var h = $('#editCodingContainer .blockContent').height();
	
	if(h > 50) {
		$('.editCodingLoadingContent').height(h + 13);
	} else {
		$('.editCodingLoadingContent').height(180);
	}
	
	$('.editCodingLoadingContent').width($('.editCodingHolder').width());
	
};
