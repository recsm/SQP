

   function do_action(action, id) {
   		 /* This is a bit ok a hack that allows a button on a row in the change list to call
   		  * an admin action on that row. It works by setting up a form and appending it to the body,
   		  * then submitting that form
   		  */
         var csrf = django.jQuery('input[name="csrfmiddlewaretoken"]').val();
		 
		 django.jQuery(document.body).append('<form id="custom_action_form" method="post">');
		 form = django.jQuery('#custom_action_form');
		
		 django.jQuery(form).append('<input type="hidden" name="csrfmiddlewaretoken" value="' + csrf +'">');
         django.jQuery(form).append('<input type="hidden" name="action" value="' + action +'">');
		 django.jQuery(form).append('<input type="hidden" name="_selected_action" value="'+ id +  '" />');
		 
		 form.submit();
		 

    }
	
	