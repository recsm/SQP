

//Tke the nodes property of an object and map the the properties to dom nodes
sqpBackbone.helpers.updateAssignedCount = function sqpBackbone$updateAssignedCount(assignedQuestionsCollection) {
	var complete = 0;
	
	assignedQuestionsCollection.each(function(assignedQuestion){
		if (assignedQuestion.get('completeness') == 'completely-coded') complete += 1;
	});
	$('.assignedQuestionsCountComplete').html(complete);
	$('.assignedQuestionsCountTotal').html(assignedQuestionsCollection.length);
	if (complete == assignedQuestionsCollection.length){
		$('#removeAssigment').show();
	}
}