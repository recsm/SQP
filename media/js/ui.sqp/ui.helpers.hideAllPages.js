



sqpBackbone.helpers.hideAllPages = function sqpBackbone$hideAllPages(){	
	$('.uiPage').hide();	
	$('#codinglist').html('');
	$('#questionDetailContainer').html('');
	$('#editCodingContainer').html('');
	$('#questionEditContainer').html('');
	$('#questionNewContainer').html('');
	$('.toptabs.selectedtab').removeClass('selectedtab').addClass('unselectedtab');
};