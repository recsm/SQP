


function hide_input(id) {
	o = document.getElementById(id).parentNode.parentNode;
	o.style.visibility = 'hidden'
	o.style.position = 'absolute'
}

function show_input(id)
{
	o = document.getElementById(id).parentNode.parentNode
	o.style.visibility = 'visible'
	o.style.position = 'static'
}

function hide_all(){
	hide_input('id_new_value');
	hide_input('id_new_value_by_related_lang');
	hide_input('id_new_value_by_related_country');
	hide_input('id_delete_coding');
}

function show_selected_change_type()
{
	switch(document.getElementById('id_change_type').value){
			case ''   : break;
			case '1'  :  show_input('id_new_value'); break;
			case '2'  :  show_input('id_new_value_by_related_lang');show_input('id_new_value_by_related_country'); break;
			case '3'  :  break;
		}
}

window.onload = function() {
	hide_all()
	show_selected_change_type()

	document.getElementById('id_change_type').onchange = function() {
		hide_all()
		show_selected_change_type()
		
	} 
}