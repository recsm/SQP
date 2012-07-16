function skipto(from_id, to_id, disable) {
   var prev_disabled = $$('div.coding.disabled_by_' + from_id),
       next_coding   = $(from_id).next('.coding')
       i = 0;
   for (i=0; i<prev_disabled.length; i++) {
     enable_coding(prev_disabled[i], from_id);
   }
   while (next_coding != null && next_coding.id != to_id) {
      disable_coding(next_coding, from_id);
      next_coding = next_coding.next('.coding');
   }
}
function disable_coding(coding_obj, disabled_by_id) {            
   var form_elts = coding_obj.getElementsBySelector('input,select,textarea')
       dontneed  = coding_obj.down('.dontneed'), 
       i = 0;
   coding_obj.addClassName('disabled');
   coding_obj.addClassName('disabled_by_' + disabled_by_id);
   for (i=0; i<form_elts.length; i++) {
      form_elts[i].disabled = true;
   }
   //dontneed.style.display = 'inline';
}
function enable_coding(coding_obj, disabled_by_id) {            
   var form_elts = coding_obj.getElementsBySelector('input,select,textarea')
       dontneed  = coding_obj.down('.dontneed'), 
       i = 0;
   coding_obj.removeClassName('disabled');
   coding_obj.removeClassName('disabled_by_' + disabled_by_id);
   for (var i=0; i<form_elts.length; i++) {
      form_elts[i].disabled = false;
   }
   //dontneed.style.display = 'none';
}


