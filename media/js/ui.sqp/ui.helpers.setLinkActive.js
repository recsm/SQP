

sqpBackbone.helpers.setLinkActive = function sqpBackbone$setLinkActive(node, state) {
	if(state) {
		node.removeClass('linkDisabled').addClass('linkActive');
	} else {
		node.removeClass('linkActive').addClass('linkDisabled');
	}
}
